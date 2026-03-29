"""
DISEASCAN - Skin Disease Classification Preprocessing Pipeline
Stages: raw → cleaned → enhanced → augmented
"""

import os
import cv2
import shutil
import logging
import numpy as np
import pandas as pd
from PIL import Image
import imagehash
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────

RAW_DIR       = "final_dataset"
CLEANED_DIR   = "stage_cleaned"
ENHANCED_DIR  = "stage_enhanced"
AUGMENTED_DIR = "stage_augmented"
LOG_FILE      = "pipeline.log"

CLASSES = ["akiec", "bcc", "bkl", "df", "melanoma", "nevus", "vasc"]

# Class tier assignment
MINORITY  = {"df", "vasc"}
MEDIUM    = {"akiec", "bkl", "bcc"}
MAJORITY  = {"melanoma", "nevus"}

# Thresholds
BLUR_THRESHOLD          = 15.0    # Laplacian variance below this → remove
NOISE_THRESHOLD         = 8.0     # Std of high-freq residual above this → denoise
DARK_THRESHOLD          = 60      # Mean brightness below this → brighten
BRIGHT_THRESHOLD        = 210     # Mean brightness above this → skip enhancement
CONTRAST_THRESHOLD      = 45      # Std of pixel values below this → CLAHE
IMAGE_SIZE = (380, 380)  # EfficientNet friendly

# Augmentation targets (final count per class after augmentation)
AUG_TARGETS = {
    "df":       5000,
    "vasc":     5000,
    "akiec":    6000,
    "bkl":      6000,
    "bcc":      7000,
    "nevus":    14000,
    "melanoma": 14000,
}

MAX_WORKERS = 8

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────

def build_hash_index():
    items = collect_images(RAW_DIR)
    unique_items = []
    seen_hashes = []

    for cls, fname, path in tqdm(items, desc="Removing duplicates"):
        phash = compute_phash(path)

        if phash is None:
            continue

        is_dup = False
        for existing in seen_hashes:
            if phash - existing <= 5:  # similarity threshold
                is_dup = True
                break

        if not is_dup:
            seen_hashes.append(phash)
            unique_items.append((cls, fname, path))

    return unique_items

def compute_phash(path: str):
    try:
        img = Image.open(path).convert("RGB")
        return imagehash.phash(img)
    except Exception:
        return None

def setup_dirs(*dirs):
    for d in dirs:
        for cls in CLASSES:
            Path(os.path.join(d, cls)).mkdir(parents=True, exist_ok=True)


def collect_images(base_dir: str) -> list[tuple[str, str, str]]:
    items = []
    for cls in CLASSES:
        cls_dir = os.path.join(base_dir, cls)
        if not os.path.isdir(cls_dir):
            continue
        for fname in os.listdir(cls_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                items.append((cls, fname, os.path.join(cls_dir, fname)))
    return items


def class_stats(base_dir: str) -> dict[str, int]:
    stats = {}
    for cls in CLASSES:
        cls_dir = os.path.join(base_dir, cls)
        if os.path.isdir(cls_dir):
            stats[cls] = len([
                f for f in os.listdir(cls_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ])
        else:
            stats[cls] = 0
    return stats


def print_stats(label: str, stats: dict[str, int]):
    log.info(f"\n{'─'*40}")
    log.info(f"  {label}")
    log.info(f"{'─'*40}")
    total = 0
    for cls in CLASSES:
        n = stats.get(cls, 0)
        total += n
        log.info(f"  {cls:<10}: {n:>6}")
    log.info(f"  {'TOTAL':<10}: {total:>6}")
    log.info(f"{'─'*40}\n")

def resize_with_padding(img: np.ndarray, size=(300, 300)) -> np.ndarray:
    h, w = img.shape[:2]

    scale = min(size[0] / h, size[1] / w)
    new_h, new_w = int(h * scale), int(w * scale)

    resized = cv2.resize(img, (new_w, new_h))

    canvas = np.zeros((size[0], size[1], 3), dtype=np.uint8)

    y_offset = (size[0] - new_h) // 2
    x_offset = (size[1] - new_w) // 2

    canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

    return canvas


# ─────────────────────────────────────────────
#  IMAGE QUALITY CHECKS
# ─────────────────────────────────────────────

def load_image(path: str) -> np.ndarray | None:
    try:
        img = cv2.imread(path)
        if img is None or img.size == 0:
            return None
        return img
    except Exception:
        return None


def blur_score(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def noise_score(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    residual = gray - blurred
    return float(np.std(residual))


def brightness_mean(img: np.ndarray) -> float:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return float(np.mean(hsv[:, :, 2]))


def contrast_std(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(np.std(gray))


# ─────────────────────────────────────────────
#  STAGE 1 — CLEAN
# ─────────────────────────────────────────────

def clean_worker(args):
    cls, fname, src_path = args
    dest_path = os.path.join(CLEANED_DIR, cls, fname)

    img = load_image(src_path)
    if img is None:
        return "corrupt", cls, fname

    score = blur_score(img)
    # Minority classes: only remove severely blurry (stricter threshold)
    effective_threshold = BLUR_THRESHOLD * 0.6 if cls in MINORITY else BLUR_THRESHOLD
    if score < effective_threshold:
        return "blurry", cls, fname

    shutil.copy2(src_path, dest_path)
    return "ok", cls, fname


def stage_clean():
    log.info("=" * 52)
    log.info("  STAGE 1: CLEANING")
    log.info("=" * 52)

    setup_dirs(CLEANED_DIR)
    items = build_hash_index()

    counts = {"ok": 0, "corrupt": 0, "blurry": 0}
    corrupt_log = []
    blurry_log  = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(clean_worker, item): item for item in items}
        with tqdm(total=len(futures), desc="Cleaning", unit="img") as pbar:
            for future in as_completed(futures):
                status, cls, fname = future.result()
                counts[status] += 1
                if status == "corrupt":
                    corrupt_log.append({"class": cls, "file": fname})
                elif status == "blurry":
                    blurry_log.append({"class": cls, "file": fname})
                pbar.update(1)

    if corrupt_log:
        pd.DataFrame(corrupt_log).to_csv("log_corrupt.csv", index=False)
    if blurry_log:
        pd.DataFrame(blurry_log).to_csv("log_blurry.csv", index=False)

    log.info(f"Kept     : {counts['ok']}")
    log.info(f"Corrupt  : {counts['corrupt']}  → log_corrupt.csv")
    log.info(f"Blurry   : {counts['blurry']}   → log_blurry.csv")
    print_stats("After Cleaning", class_stats(CLEANED_DIR))


# ─────────────────────────────────────────────
#  STAGE 2 — ENHANCE
# ─────────────────────────────────────────────

def apply_denoising(img: np.ndarray, cls: str) -> np.ndarray:
    # Preserve fine melanoma features — lighter denoising
    h = 5 if cls == "melanoma" else 8
    return cv2.fastNlMeansDenoisingColored(img, None, h, h, 7, 21)


def apply_brightness(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    mean_v = np.mean(hsv[:, :, 2])
    if mean_v < 10:
        return img
    scale = min(DARK_THRESHOLD / mean_v * 1.15, 1.5)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * scale, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def apply_clahe(img: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def enhance_worker(args):
    cls, fname, src_path = args
    dest_path = os.path.join(ENHANCED_DIR, cls, fname)

    img = load_image(src_path)
    if img is None:
        return "error", cls, fname

    ops = []
    bri = brightness_mean(img)
    con = contrast_std(img)
    noi = noise_score(img)

    if noi > NOISE_THRESHOLD:
        img = apply_denoising(img, cls)
        ops.append("denoise")

    if bri < DARK_THRESHOLD and bri > 5:
        img = apply_brightness(img)
        ops.append("brighten")

    if con < CONTRAST_THRESHOLD:
        img = apply_clahe(img)
        ops.append("clahe")

    # RESIZE BEFORE SAVING
    img = resize_with_padding(img, IMAGE_SIZE)
    cv2.imwrite(dest_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return ("enhanced" if ops else "passthrough"), cls, fname


def stage_enhance():
    log.info("=" * 52)
    log.info("  STAGE 2: ENHANCEMENT")
    log.info("=" * 52)

    setup_dirs(ENHANCED_DIR)
    items = collect_images(CLEANED_DIR)

    counts = {"enhanced": 0, "passthrough": 0, "error": 0}
    enhanced_log = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(enhance_worker, item): item for item in items}
        with tqdm(total=len(futures), desc="Enhancing", unit="img") as pbar:
            for future in as_completed(futures):
                status, cls, fname = future.result()
                counts[status] = counts.get(status, 0) + 1
                if status == "enhanced":
                    enhanced_log.append({"class": cls, "file": fname})
                pbar.update(1)

    if enhanced_log:
        pd.DataFrame(enhanced_log).to_csv("log_enhanced.csv", index=False)

    log.info(f"Enhanced    : {counts['enhanced']}  → log_enhanced.csv")
    log.info(f"Passthrough : {counts['passthrough']}")
    log.info(f"Errors      : {counts['error']}")
    print_stats("After Enhancement", class_stats(ENHANCED_DIR))


# ─────────────────────────────────────────────
#  STAGE 3 — AUGMENTATION
# ─────────────────────────────────────────────
import random 
def augment_minority(img: np.ndarray, idx: int) -> np.ndarray:
    h, w = img.shape[:2]
    ops = [
        lambda x: cv2.flip(x, 1),
        lambda x: cv2.flip(x, 0),
        lambda x: cv2.rotate(x, cv2.ROTATE_90_CLOCKWISE),
        lambda x: cv2.rotate(x, cv2.ROTATE_90_COUNTERCLOCKWISE),
        lambda x: cv2.rotate(x, cv2.ROTATE_180),
        lambda x: _zoom(x, np.random.uniform(0.85, 1.15)),
        lambda x: _brightness_jitter(x, np.random.uniform(0.75, 1.30)),
        lambda x: _add_noise(x, sigma=np.random.uniform(2, 6)),
        lambda x: cv2.GaussianBlur(x, (3, 3), 0),
    ]
    chosen = random.choice(ops)
    return chosen(img)


def augment_medium(img: np.ndarray, idx: int) -> np.ndarray:
    ops = [
        lambda x: cv2.flip(x, 1),
        lambda x: cv2.rotate(x, cv2.ROTATE_90_CLOCKWISE),
        lambda x: cv2.rotate(x, cv2.ROTATE_90_COUNTERCLOCKWISE),
        lambda x: _brightness_jitter(x, np.random.uniform(0.85, 1.15)),
        lambda x: _zoom(x, np.random.uniform(0.9, 1.1)),
    ]
    chosen = random.choice(ops)
    return chosen(img)


def augment_majority(img: np.ndarray, idx: int) -> np.ndarray:
    ops = [
        lambda x: cv2.flip(x, 1),
        lambda x: cv2.flip(x, 0),
    ]
    chosen = random.choice(ops)
    return chosen(img)


def _zoom(img: np.ndarray, factor: float) -> np.ndarray:
    h, w = img.shape[:2]
    new_h, new_w = int(h * factor), int(w * factor)
    resized = cv2.resize(img, (new_w, new_h))
    if factor > 1.0:
        y = (new_h - h) // 2
        x = (new_w - w) // 2
        return resized[y:y+h, x:x+w]
    else:
        canvas = np.zeros_like(img)
        y = (h - new_h) // 2
        x = (w - new_w) // 2
        canvas[y:y+new_h, x:x+new_w] = resized
        return canvas


def _brightness_jitter(img: np.ndarray, factor: float) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def _add_noise(img: np.ndarray, sigma: float) -> np.ndarray:
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    noisy = np.clip(img.astype(np.float32) + noise, 0, 255)
    return noisy.astype(np.uint8)


def augment_class(cls: str):
    src_dir  = os.path.join(ENHANCED_DIR, cls)
    dest_dir = os.path.join(AUGMENTED_DIR, cls)
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    images = [
        f for f in os.listdir(src_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    # Copy originals first
    for fname in images:
        shutil.copy2(os.path.join(src_dir, fname), os.path.join(dest_dir, fname))

    current = len(images)
    target  = AUG_TARGETS.get(cls, current)

    if current >= target:
        log.info(f"  {cls}: {current} images — target met, no augmentation needed")
        return

    needed = target - current
    if cls in MINORITY:
        aug_fn = augment_minority
    elif cls in MEDIUM:
        aug_fn = augment_medium
    else:
        aug_fn = augment_majority

    generated = 0
    idx = 0
    paths = [os.path.join(src_dir, f) for f in images]

    while generated < needed:
        src_path = paths[generated % len(paths)]
        img = load_image(src_path)
        if img is None:
            generated += 1
            idx += 1
            continue
        aug_img = aug_fn(img, idx)
        base = os.path.splitext(os.path.basename(src_path))[0]
        out_name = f"{base}_aug{generated}.jpg"
        cv2.imwrite(
            os.path.join(dest_dir, out_name),
            aug_img,
            [cv2.IMWRITE_JPEG_QUALITY, 92]
        )
        generated += 1
        idx += 1

    log.info(f"  {cls}: {current} → {current + generated} (+{generated} augmented)")


def stage_augment():
    log.info("=" * 52)
    log.info("  STAGE 3: AUGMENTATION")
    log.info("=" * 52)

    for cls in tqdm(CLASSES, desc="Augmenting classes"):
        augment_class(cls)

    print_stats("After Augmentation", class_stats(AUGMENTED_DIR))


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    log.info("\n" + "=" * 52)
    log.info("  DISEASCAN — Full Preprocessing Pipeline")
    log.info("=" * 52 + "\n")

    print_stats("RAW Dataset", class_stats(RAW_DIR))

    stage_clean()
    stage_enhance()
    stage_augment()

    log.info("\n  Pipeline complete.")
    log.info(f"    Cleaned   → {CLEANED_DIR}/")
    log.info(f"    Enhanced  → {ENHANCED_DIR}/")
    log.info(f"    Augmented → {AUGMENTED_DIR}/")
    log.info(f"    Logs      → pipeline.log, log_corrupt.csv, log_blurry.csv, log_enhanced.csv")


if __name__ == "__main__":
    main()
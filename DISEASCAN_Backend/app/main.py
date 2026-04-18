"""
FastAPI backend — Skin Lesion Prediction Service  v2.0
POST /predict  →  validated image → stabilised inference → enriched response

New in v2:
  • Strict image validation  (JPEG/PNG only, ≤5 MB, corruption-safe)
  • Precise per-stage latency breakdown  (ms)
  • Confidence interpretation  (High / Moderate / Low)
  • Probability normalisation
  • Medical disclaimer  (every response)
  • Stability note  (templated, no model changes)
  • heatmap_url placeholder  (null for now, ready for Grad-CAM)
  • Hardened error handling with correct HTTP status codes
  • Default num_runs=3, overridable up to 5

Project layout:
  .
  ├── main.py               ← this file
  ├── stable_inference.py
  ├── class_metadata.py
  └── requirements.txt
"""

import asyncio
import io
import logging
import struct
import time
import zlib
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field

from class_metadata import LESION_MAP, enrich_predictions
from stable_inference import stable_predict

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════
CLASS_NAMES  = list(LESION_MAP.keys())    # ["akiec","bcc","bkl","df","mel","nv","vasc"]
CLASS_INDEX  = {name: i for i, name in enumerate(CLASS_NAMES)}   # O(1) label → index
MAX_FILE_BYTES = 5 * 1024 * 1024           # 5 MB
ALLOWED_MIME   = {"image/jpeg", "image/png"}
ALLOWED_MAGIC  = {
    b"\xff\xd8\xff": "image/jpeg",         # JPEG magic bytes
    b"\x89PNG":      "image/png",          # PNG magic bytes
}

MEDICAL_DISCLAIMER = (
    "This tool is intended for informational and research purposes only. "
    "It does not constitute medical advice, diagnosis, or treatment. "
    "Always consult a qualified dermatologist or healthcare professional "
    "for any skin-related concerns. AI predictions may be inaccurate."
)


# ═════════════════════════════════════════════════════════════════════════════
# MODEL LIFECYCLE  —  replace load_model() and build_model_fn() only
# ═════════════════════════════════════════════════════════════════════════════
MODEL    = None
MODEL_FN = None


def load_model():
    """
    Loads diseascan_model.keras with custom objects WarmupCosineDecay and
    FocalLoss, which must live in  DISEASCAN/custom_keras_objects.py
    relative to this file's parent directory.

    Expected project layout:
        DISEASCAN/
        ├── custom_keras_objects.py   ← WarmupCosineDecay, FocalLoss
        └── app/
            ├── main.py               ← this file
            └── models/
                └── diseascan_model.keras
    """
    import os
    import sys
    import tensorflow as tf

    # ── Locate custom_keras_objects.py ───────────────────────────────────
    # Walks up from this file to the DISEASCAN root so the import works
    # regardless of the working directory uvicorn is launched from.
    here      = os.path.dirname(os.path.abspath(__file__))
    diseascan = os.path.abspath(os.path.join(here, "..", "..", "DISEASCAN"))
    if not os.path.isdir(diseascan):
        # Fallback: try the immediate parent (flat layout)
        diseascan = os.path.abspath(os.path.join(here, ".."))

    if diseascan not in sys.path:
        sys.path.insert(0, diseascan)

    try:
        from custom_keras_objects import FocalLoss, WarmupCosineDecay
        log.info("Custom objects loaded: WarmupCosineDecay, FocalLoss")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"Could not import custom_keras_objects from '{diseascan}'. "
            "Check that DISEASCAN/custom_keras_objects.py exists and that "
            "WarmupCosineDecay and FocalLoss are defined there."
        ) from exc

    # ── Model path ────────────────────────────────────────────────────────
    model_path = os.path.join(here, "models", "diseascan_model.keras")
    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            f"Model file not found at '{model_path}'. "
            "Copy diseascan_model.keras into app/models/ and restart."
        )

    log.info(f"Loading model from: {model_path}")
    model = tf.keras.models.load_model(
        model_path,
        custom_objects={
            "WarmupCosineDecay": WarmupCosineDecay,
            "FocalLoss":         FocalLoss,
        },
    )

    # Warm-up pass — forces TF to compile the graph before the first request
    # so the first real prediction isn't penalised by JIT compilation latency.
    dummy = np.zeros((1, 380, 380, 3), dtype=np.float32)
    model(dummy, training=False)
    log.info("Warm-up pass complete. Model is ready.")

    return model


def build_model_fn(model):
    """
    Returns a single-argument callable:
        fn(img: np.ndarray uint8 H×W×3) → np.ndarray float32 (7,)

    Pipeline (must exactly mirror training):
      1. Resize to 380×380  (model's expected input resolution)
      2. Cast to float32
      3. EfficientNet preprocess_input  (scales pixels to [-1, 1])
      4. Add batch dimension
      5. Forward pass with training=False  (disables dropout / BN update)
      6. Return softmax probabilities as a 1-D numpy array
    """
    from tensorflow.keras.applications.efficientnet import preprocess_input

    TARGET = (380, 380)

    def fn(img: np.ndarray) -> np.ndarray:
        # 1 — resize  (PIL BILINEAR matches tf.image.resize default quality)
        pil_img = Image.fromarray(img.astype(np.uint8)).resize(TARGET, Image.BILINEAR)

        # 2 & 3 — float32 + EfficientNet normalisation  ([-1, 1] range)
        x = preprocess_input(np.array(pil_img, dtype=np.float32))

        # 4 — batch axis:  (380, 380, 3) → (1, 380, 380, 3)
        x = np.expand_dims(x, axis=0)

        # 5 — inference  (training=False → eval mode, no graph update)
        preds = model(x, training=False)

        # 6 — to numpy, drop batch dim → shape (7,)
        return preds.numpy()[0]

    return fn


@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODEL, MODEL_FN
    log.info("Loading model …")
    try:
        MODEL    = load_model()
        MODEL_FN = build_model_fn(MODEL)
        log.info("Model ready.")
    except NotImplementedError as exc:
        log.warning(f"Model stub not implemented: {exc}  →  /predict returns 503.")
    except Exception as exc:
        log.error(f"Model failed to load: {exc}  →  /predict returns 503.")
    yield
    log.info("Shutdown complete.")


# ═════════════════════════════════════════════════════════════════════════════
# APP
# ═════════════════════════════════════════════════════════════════════════════
app = FastAPI(
    title="Skin Lesion Classifier API",
    description=(
        "Stabilised multi-run dermoscopy inference with per-class clinical metadata.\n\n"
        f"⚠️  {MEDICAL_DISCLAIMER}"
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═════════════════════════════════════════════════════════════════════════════
# IMAGE VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

def _check_magic_bytes(raw: bytes) -> str:
    """Return detected MIME type or raise 415 if not JPEG/PNG."""
    for magic, mime in ALLOWED_MAGIC.items():
        if raw[: len(magic)] == magic:
            return mime
    raise HTTPException(
        status_code=415,
        detail="Unsupported file format. Only JPEG and PNG images are accepted.",
    )


def _check_png_integrity(raw: bytes) -> None:
    """Walk every PNG chunk and verify CRC — raises 422 on corruption."""
    try:
        pos = 8                                  # skip PNG signature
        while pos < len(raw):
            length     = struct.unpack(">I", raw[pos : pos + 4])[0]
            chunk_type = raw[pos + 4 : pos + 8]
            data       = raw[pos + 8 : pos + 8 + length]
            stored_crc = struct.unpack(">I", raw[pos + 8 + length : pos + 12 + length])[0]
            computed   = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
            if stored_crc != computed:
                raise ValueError("CRC mismatch")
            pos += 12 + length
            if chunk_type == b"IEND":
                break
    except (struct.error, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Corrupted PNG file: {exc}")


def validate_and_decode(raw: bytes, filename: str) -> np.ndarray:
    """
    Full validation pipeline:
      1. Empty-file guard
      2. Size gate  (≤ 5 MB)
      3. Magic-byte MIME detection  (JPEG / PNG only)
      4. PNG CRC integrity check
      5. PIL decode with corruption guard
      6. Convert to RGB at original resolution — NO resize

    Resizing to the model's input size (380×380) is done exclusively inside
    build_model_fn so the image is downsampled only once.
    Returns uint8 numpy array (H, W, 3).
    """
    # 1 — empty file
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Empty file received.")

    # 2 — size
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File too large ({len(raw) / 1_048_576:.1f} MB). "
                "Maximum allowed size is 5 MB."
            ),
        )

    # 3 — magic bytes (true format, ignoring client Content-Type)
    detected_mime = _check_magic_bytes(raw)

    # 4 — PNG CRC integrity
    if detected_mime == "image/png":
        _check_png_integrity(raw)

    # 5 — PIL decode (catches truncated / partial files)
    try:
        probe = Image.open(io.BytesIO(raw))
        probe.verify()                           # exhaustive check; closes file pointer
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=422,
            detail="Cannot identify image. The file may be corrupted or incomplete.",
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Image verification failed: {exc}")

    # Re-open after verify() (verify() makes the object unusable).
    # NO resize here — resizing to 380×380 is done inside build_model_fn
    # so the image is only ever downsampled once (original → 380×380).
    # A 224 → 380 upscale would introduce interpolation distortion that
    # degrades prediction quality.
    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Image decoding failed: {exc}")

    return np.array(img, dtype=np.uint8)


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def normalise_probs(probs: np.ndarray) -> np.ndarray:
    """Clip negatives, re-normalise to exactly 1.0."""
    probs = np.clip(probs, 0.0, None)
    total = probs.sum()
    if total == 0:
        raise HTTPException(status_code=500, detail="Model returned all-zero probabilities.")
    return probs / total


def confidence_label(score: float) -> str:
    if score >= 0.75:
        return "High confidence"
    if score >= 0.40:
        return "Moderate confidence"
    return "Low confidence"


def stability_note(num_runs: int) -> str:
    noun = "run" if num_runs == 1 else "runs"
    return (
        f"Prediction averaged over {num_runs} independent inference {noun} "
        "to reduce stochastic variance and improve stability."
    )


class _Timer:
    """Lightweight multi-stage wall-clock recorder (milliseconds)."""

    def __init__(self):
        self._t0:    float       = time.perf_counter()
        self._marks: dict[str, float] = {}

    def mark(self, name: str) -> None:
        self._marks[name] = (time.perf_counter() - self._t0) * 1_000

    def get(self, name: str, default: float = 0.0) -> float:
        return self._marks.get(name, default)

    @property
    def total_ms(self) -> float:
        return (time.perf_counter() - self._t0) * 1_000


# ═════════════════════════════════════════════════════════════════════════════
# RESPONSE SCHEMA
# ═════════════════════════════════════════════════════════════════════════════

class LesionDetails(BaseModel):
    name:           str
    severity:       str
    description:    str
    recommendation: str


class Top3Entry(BaseModel):
    rank:              int
    code:              str
    name:              str
    confidence:        float
    confidence_label:  str
    severity:          str


class LatencyBreakdown(BaseModel):
    validation_ms: float = Field(..., description="Image validation + decode time")
    inference_ms:  float = Field(..., description="Model forward passes + averaging time")
    total_ms:      float = Field(..., description="End-to-end request time")


class PredictResponse(BaseModel):
    prediction:         str           = Field(..., description="Top-1 class code, e.g. 'mel'")
    confidence:         float         = Field(..., description="Normalised top-1 probability (0–1)")
    confidence_label:   str           = Field(..., description="High / Moderate / Low confidence")
    top3:               list[Top3Entry]
    details:            LesionDetails
    stability_note:     str           = Field(..., description="Multi-run averaging summary")
    num_runs:           int           = Field(..., description="Inference runs averaged")
    heatmap_url:        Optional[str] = Field(None, description="Grad-CAM visualisation URL (null until implemented)")
    medical_disclaimer: str
    latency:            LatencyBreakdown


# ═════════════════════════════════════════════════════════════════════════════
# /predict ENDPOINT
# ═════════════════════════════════════════════════════════════════════════════

@app.post(
    "/predict",
    response_model=PredictResponse,
    summary="Classify a skin lesion image",
    responses={
        200: {"description": "Successful stabilised prediction"},
        400: {"description": "Empty or malformed file"},
        413: {"description": "File exceeds the 5 MB limit"},
        415: {"description": "Unsupported file type — send JPEG or PNG"},
        422: {"description": "Image is corrupted or unreadable"},
        500: {"description": "Model inference failure"},
        503: {"description": "Model not loaded — implement load_model()"},
    },
)
async def predict(
    file: UploadFile = File(..., description="Dermoscopy image (JPEG or PNG, max 5 MB)"),
    num_runs: int    = Query(
        default=3,
        ge=3,
        le=5,
        description="Number of inference runs to average. 3 = fast, 5 = most stable.",
    ),
):
    """
    **Pipeline**
    1. Validate file  (type, size, magic bytes, PNG CRC, PIL decode).
    2. Run `stable_predict` — *num_runs* forward passes, averaged probabilities.
    3. Normalise probabilities so they sum to exactly 1.
    4. Enrich top-3 predictions with clinical metadata.
    5. Return structured JSON with latency breakdown and medical disclaimer.
    """
    # ── Model availability ────────────────────────────────────────────────
    if MODEL_FN is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model is not available. "
                "Implement load_model() and build_model_fn() in main.py."
            ),
        )

    # ── Declared MIME type (first gate, before reading bytes) ─────────────
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Content-Type '{file.content_type}' is not allowed. "
                "Upload an image/jpeg or image/png file."
            ),
        )

    timer = _Timer()

    # ── Read + deep validation ────────────────────────────────────────────
    raw = await file.read()
    await file.close()
    image = validate_and_decode(raw, file.filename or "upload")
    timer.mark("validation_ms")

    # ── Inference (non-blocking) ──────────────────────────────────────────
    # TensorFlow is CPU/GPU-bound and not async-aware. Running it directly
    # in the coroutine would block the entire event loop for every request,
    # serialising all concurrent callers.  run_in_executor() delegates the
    # work to a thread from the default ThreadPoolExecutor so FastAPI can
    # continue serving other requests while inference runs.
    try:
        loop   = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,           # default ThreadPoolExecutor (matches CPU core count)
            lambda: stable_predict(
                model_fn=MODEL_FN,
                image=image,
                class_names=CLASS_NAMES,
                num_runs=num_runs,
                top_k=3,
            ),
        )
    except MemoryError:
        raise HTTPException(status_code=500, detail="Server ran out of memory during inference.")
    except Exception as exc:
        log.exception("Inference failed")
        raise HTTPException(status_code=500, detail=f"Inference error: {exc}")

    timer.mark("inference_ms")

    # ── Normalise ─────────────────────────────────────────────────────────
    avg_norm = normalise_probs(result.averaged_probs)
    for pred in result.top_predictions:
        pred.confidence = float(avg_norm[CLASS_INDEX[pred.label]])   # O(1) dict lookup

    # ── Enrich with clinical metadata ─────────────────────────────────────
    enriched = enrich_predictions(result.top_predictions)
    best     = enriched[0]

    # ── Assemble response ─────────────────────────────────────────────────
    response = PredictResponse(
        prediction=best["code"],
        confidence=round(best["confidence"], 6),
        confidence_label=confidence_label(best["confidence"]),
        top3=[
            Top3Entry(
                rank=e["rank"],
                code=e["code"],
                name=e["full_name"],
                confidence=round(e["confidence"], 6),
                confidence_label=confidence_label(e["confidence"]),
                severity=e["severity"],
            )
            for e in enriched
        ],
        details=LesionDetails(
            name=best["full_name"],
            severity=best["severity"],
            description=best["description"],
            recommendation=best["recommendation"],
        ),
        stability_note=stability_note(num_runs),
        num_runs=num_runs,
        heatmap_url=None,
        medical_disclaimer=MEDICAL_DISCLAIMER,
        latency=LatencyBreakdown(
            # timer marks are cumulative (ms since request start), so each
            # stage duration = current_mark - previous_mark.
            validation_ms=round(timer.get("validation_ms"), 2),
            inference_ms=round(
                timer.get("inference_ms") - timer.get("validation_ms"), 2
            ),
            total_ms=round(timer.total_ms, 2),
        ),
    )

    log.info(
        "[%s] → %s (%.2f%%)  %s  runs=%d  total=%.1fms",
        file.filename,
        best["code"],
        best["confidence"] * 100,
        confidence_label(best["confidence"]),
        num_runs,
        timer.total_ms,
    )

    return response


# ═════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/health", include_in_schema=False)
async def health():
    return {
        "status":        "ok",
        "model_loaded":  MODEL_FN is not None,
        "max_file_mb":   MAX_FILE_BYTES // 1_048_576,
        "allowed_types": sorted(ALLOWED_MIME),
        "classes":       CLASS_NAMES,
    }


# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL FALLBACK HANDLER
# ═════════════════════════════════════════════════════════════════════════════

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    log.exception("Unhandled exception on %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )

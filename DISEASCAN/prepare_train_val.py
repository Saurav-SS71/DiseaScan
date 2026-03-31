"""
Prepare Train/Val Split
Splits stage_augmented/ into train/ and val/ directories (80/20 split)
"""

import os
import shutil
from pathlib import Path
import random

SEED = 42
random.seed(SEED)

SOURCE_DIR = "stage_augmented"
TRAIN_DIR = "train"
VAL_DIR = "val"
SPLIT_RATIO = 0.8  # 80% train, 20% val

CLASSES = ["akiec", "bcc", "bkl", "df", "melanoma", "nevus", "vasc"]

def setup_directories():
    """Create train/val class subdirectories."""
    for class_name in CLASSES:
        os.makedirs(os.path.join(TRAIN_DIR, class_name), exist_ok=True)
        os.makedirs(os.path.join(VAL_DIR, class_name), exist_ok=True)
    print(f"Created {TRAIN_DIR}/ and {VAL_DIR}/ with class subdirectories.")

def split_class_images(class_name):
    """Split images of a single class into train/val."""
    source_class_dir = os.path.join(SOURCE_DIR, class_name)
    images = os.listdir(source_class_dir)
    
    random.shuffle(images)
    split_idx = int(len(images) * SPLIT_RATIO)
    train_images = images[:split_idx]
    val_images = images[split_idx:]
    
    # Copy train images
    for img in train_images:
        src = os.path.join(source_class_dir, img)
        dst = os.path.join(TRAIN_DIR, class_name, img)
        shutil.copy2(src, dst)
    
    # Copy val images
    for img in val_images:
        src = os.path.join(source_class_dir, img)
        dst = os.path.join(VAL_DIR, class_name, img)
        shutil.copy2(src, dst)
    
    print(f"  {class_name:12} → train: {len(train_images):5}  val: {len(val_images):5}")
    return len(train_images), len(val_images)

def main():
    print("=" * 60)
    print("  Preparing Train/Val Split (80/20)")
    print("=" * 60)
    
    if not os.path.isdir(SOURCE_DIR):
        print(f"Error: {SOURCE_DIR}/ not found!")
        return
    
    setup_directories()
    print("\nSplitting images by class:")
    
    total_train = total_val = 0
    for class_name in CLASSES:
        train_count, val_count = split_class_images(class_name)
        total_train += train_count
        total_val += val_count
    
    print("\n" + "=" * 60)
    print(f"  TOTAL TRAIN: {total_train:,}")
    print(f"  TOTAL VAL  : {total_val:,}")
    print("=" * 60)
    print("Dataset split complete!")
    print(f"   train/ → {TRAIN_DIR}/")
    print(f"   val/   → {VAL_DIR}/")

if __name__ == "__main__":
    main()

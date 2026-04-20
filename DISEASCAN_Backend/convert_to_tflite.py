"""
One-time script: Convert diseascan_model.keras → diseascan_model.tflite

Run this LOCALLY (not on Render) — it needs full TensorFlow installed.

Usage:
    python convert_to_tflite.py

Output:
    app/models/diseascan_model.tflite
"""

import os
import sys

# ── Locate custom_keras_objects.py ────────────────────────────────────────────
here = os.path.dirname(os.path.abspath(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import tensorflow as tf
from custom_keras_objects import FocalLoss, WarmupCosineDecay

# ── Paths ─────────────────────────────────────────────────────────────────────
KERAS_PATH  = os.path.join(here, "app", "models", "diseascan_model.keras")
TFLITE_PATH = os.path.join(here, "app", "models", "diseascan_model.tflite")

if not os.path.isfile(KERAS_PATH):
    print(f"ERROR: Model not found at {KERAS_PATH}")
    sys.exit(1)

# ── Load the Keras model ─────────────────────────────────────────────────────
print(f"Loading Keras model from: {KERAS_PATH}")
model = tf.keras.models.load_model(
    KERAS_PATH,
    custom_objects={
        "WarmupCosineDecay": WarmupCosineDecay,
        "FocalLoss": FocalLoss,
        "DISEASCAN>WarmupCosineDecay": WarmupCosineDecay,
        "DISEASCAN>FocalLoss": FocalLoss,
    },
    compile=False,
    safe_mode=False,
)
print(f"Model loaded. Input shape: {model.input_shape}, Output shape: {model.output_shape}")

# ── Convert to TFLite ────────────────────────────────────────────────────────
print("Converting to TFLite ...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Use float16 quantization to halve the file size while keeping good accuracy
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]

tflite_model = converter.convert()

# ── Save ──────────────────────────────────────────────────────────────────────
with open(TFLITE_PATH, "wb") as f:
    f.write(tflite_model)

keras_mb  = os.path.getsize(KERAS_PATH) / 1_048_576
tflite_mb = os.path.getsize(TFLITE_PATH) / 1_048_576

print(f"\n✅ Conversion complete!")
print(f"   Keras  : {keras_mb:.1f} MB  →  {KERAS_PATH}")
print(f"   TFLite : {tflite_mb:.1f} MB  →  {TFLITE_PATH}")
print(f"   Reduction: {(1 - tflite_mb / keras_mb) * 100:.0f}%")
print(f"\nNext: commit diseascan_model.tflite and push to GitHub.")

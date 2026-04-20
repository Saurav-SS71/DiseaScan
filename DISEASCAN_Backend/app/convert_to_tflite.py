# convert_to_tflite.py
import os

# ── MUST be set before importing tensorflow ───────────────────────────────────
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import tensorflow as tf
import tf_keras  # pip install tf-keras

print("TF:", tf.__version__, "| tf_keras:", tf_keras.__version__)

class WarmupCosineDecay(tf.keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self, initial_lr, warmup_steps, total_steps, **kwargs):
        super().__init__(**kwargs)
        self.initial_lr   = initial_lr
        self.warmup_steps = warmup_steps
        self.total_steps  = total_steps

    def __call__(self, step):
        step      = tf.cast(step, tf.float32)
        warmup_lr = self.initial_lr * (step / self.warmup_steps)
        cosine_lr = self.initial_lr * 0.5 * (
            1 + tf.cos(
                tf.constant(3.14159265) *
                (step - self.warmup_steps) /
                (self.total_steps - self.warmup_steps)
            )
        )
        return tf.where(step < self.warmup_steps, warmup_lr, cosine_lr)

    def get_config(self):
        return {
            "initial_lr":   self.initial_lr,
            "warmup_steps": self.warmup_steps,
            "total_steps":  self.total_steps,
        }

KERAS_MODEL_PATH  = "app/models/diseascan_model.keras"
TFLITE_MODEL_PATH = "app/models/diseascan_model.tflite"

# ── Step 1: Load with tf_keras ────────────────────────────────────────────────
print("Loading Keras model...")
model = tf_keras.models.load_model(
    KERAS_MODEL_PATH,
    custom_objects={"WarmupCosineDecay": WarmupCosineDecay},
    compile=False
)
print(f"✅ Loaded. Input shape: {model.input_shape}")

# ── Step 2: Convert directly from tf_keras model ──────────────────────────────
print("Converting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
# Uncomment for ~4x smaller file (recommended for Render free tier):
# converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# ── Step 3: Save ──────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(TFLITE_MODEL_PATH), exist_ok=True)
with open(TFLITE_MODEL_PATH, "wb") as f:
    f.write(tflite_model)

size_mb = os.path.getsize(TFLITE_MODEL_PATH) / 1_048_576
print(f"✅ Done! Saved: {TFLITE_MODEL_PATH}  ({size_mb:.1f} MB)")
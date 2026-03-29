"""
DISEASCAN — Training Script
Run:
    python train.py
"""

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress TF warnings

import tensorflow as tf
import numpy as np

from config import (
    MODEL_DIR, EPOCHS_HEAD, EPOCHS_FINETUNE,
    LR_HEAD, LR_FINETUNE, UNFREEZE_FROM_LAYER,
    CLASS_COUNTS, SEED
)
from data_pipeline import get_datasets
from model        import build_model, unfreeze_top_layers, model_summary
from losses       import get_loss, get_metrics, compute_class_weights, FocalLoss
from callbacks    import get_callbacks

os.environ["TF_DETERMINISTIC_OPS"] = "1"
tf.random.set_seed(SEED)
np.random.seed(SEED)


# ─────────────────────────────────────────────
#  MIXED PRECISION
#  ~2× speedup on Tensor Cores (V100 / A100 / RTX).
#  No accuracy impact — loss scale handled automatically.
# ─────────────────────────────────────────────
def enable_mixed_precision():
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        policy = tf.keras.mixed_precision.Policy("mixed_float16")
        tf.keras.mixed_precision.set_global_policy(policy)
        print(f"Mixed precision enabled: {policy.name}")
    else:
        print("No GPU found — running on CPU, mixed precision skipped.")


# ─────────────────────────────────────────────
#  COSINE DECAY WITH WARMUP
#  Warmup prevents large LR updates in early steps
#  where the randomly initialised head is unstable.
# ─────────────────────────────────────────────
@tf.keras.utils.register_keras_serializable(package="DISEASCAN")
class WarmupCosineDecay(tf.keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self, initial_lr, warmup_steps, total_steps):
        super().__init__()
        self.initial_lr   = initial_lr
        self.warmup_steps = warmup_steps
        self.total_steps  = total_steps

    def __call__(self, step):
        step   = tf.cast(step, tf.float32)
        warmup = tf.cast(self.warmup_steps, tf.float32)
        total  = tf.cast(self.total_steps,  tf.float32)

        warmup_lr = self.initial_lr * (step / warmup)
        cosine_lr = self.initial_lr * 0.5 * (
            1.0 + tf.cos(np.pi * (step - warmup) / (total - warmup))
        )
        return tf.where(step < warmup, warmup_lr, cosine_lr)

    def get_config(self):
        return {
            "initial_lr":   self.initial_lr,
            "warmup_steps": self.warmup_steps,
            "total_steps":  self.total_steps,
        }


# ─────────────────────────────────────────────
#  PHASE 1 — TRAIN HEAD
# ─────────────────────────────────────────────
def train_head(train_ds, val_ds, class_weights):
    print("\n" + "=" * 60)
    print("  PHASE 1 — Training Classification Head")
    print("=" * 60)

    model = build_model(trainable_base=False)
    model_summary(model)

    steps_per_epoch = len(train_ds)
    total_steps     = steps_per_epoch * EPOCHS_HEAD
    warmup_steps    = steps_per_epoch * 2        # 2 epoch warmup

    lr_schedule = WarmupCosineDecay(
        initial_lr   = LR_HEAD,
        warmup_steps = warmup_steps,
        total_steps  = total_steps,
    )

    model.compile(
        optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule),
        loss      = get_loss(),
        metrics   = get_metrics(),
    )

    history = model.fit(
        train_ds,
        epochs          = EPOCHS_HEAD,
        validation_data = val_ds,
        class_weight    = class_weights,
        callbacks       = get_callbacks("head"),
        verbose         = 1,
    )

    # Save after phase 1
    save_path = os.path.join(MODEL_DIR, "diseascan_phase1.keras")
    model.save(save_path)
    print(f"\nPhase 1 model saved → {save_path}")

    return model, history


# ─────────────────────────────────────────────
#  PHASE 2 — FINE-TUNE TOP LAYERS
# ─────────────────────────────────────────────
def fine_tune(model, train_ds, val_ds, class_weights):
    print("\n" + "=" * 60)
    print("  PHASE 2 — Fine-Tuning Top Layers")
    print("=" * 60)

    model = unfreeze_top_layers(model, from_layer=UNFREEZE_FROM_LAYER)

    steps_per_epoch = len(train_ds)
    total_steps     = steps_per_epoch * EPOCHS_FINETUNE
    warmup_steps    = steps_per_epoch * 3        # 3 epoch warmup

    lr_schedule = WarmupCosineDecay(
        initial_lr   = LR_FINETUNE,
        warmup_steps = warmup_steps,
        total_steps  = total_steps,
    )

    # AdamW for fine-tuning — weight decay prevents catastrophic
    # forgetting of ImageNet representations
    model.compile(
        optimizer = tf.keras.optimizers.AdamW(
            learning_rate  = lr_schedule,
            weight_decay   = 1e-4,
        ),
        loss    = get_loss(),
        metrics = get_metrics(),
    )

    history = model.fit(
        train_ds,
        epochs          = EPOCHS_FINETUNE,
        validation_data = val_ds,
        class_weight    = class_weights,
        callbacks       = get_callbacks("finetune"),
        verbose         = 1,
    )

    save_path = os.path.join(MODEL_DIR, "diseascan_final.keras")
    model.save(save_path)
    print(f"\nFinal model saved → {save_path}")

    return model, history


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    enable_mixed_precision()

    print("\nBuilding data pipelines...")
    train_ds, val_ds = get_datasets()

    class_weights = compute_class_weights(CLASS_COUNTS)
    print(f"\nClass weights: {class_weights}")


    model = tf.keras.models.load_model(
        "models/diseascan_phase1.keras",
        custom_objects={
            "WarmupCosineDecay": WarmupCosineDecay,
            "FocalLoss": FocalLoss,
        }
    )
    print("Loaded Phase 1 model")

    # # Phase 1
    # model, history_head = train_head(train_ds, val_ds, class_weights)

    # Phase 2
    model, history_ft = fine_tune(model, train_ds, val_ds, class_weights)

    print("\nTraining complete.")


if __name__ == "__main__":
    main()

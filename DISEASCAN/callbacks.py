import os
import tensorflow as tf
from config import (
    MODEL_DIR, LOG_DIR,
    EARLY_STOP_PATIENCE, REDUCE_LR_PATIENCE,
    REDUCE_LR_FACTOR, MIN_LR
)


def get_callbacks(phase: str, monitor: str = "val_accuracy") -> list:
    """
    phase: "head" | "finetune"
    """
    checkpoint_path = os.path.join(MODEL_DIR, f"diseascan_{phase}_best.keras")

    callbacks = [
        # ── Save best val_accuracy checkpoint ───────────────
        tf.keras.callbacks.ModelCheckpoint(
            filepath        = checkpoint_path,
            monitor         = monitor,
            save_best_only  = True,
            save_weights_only=False,
            mode            = "max",
            verbose         = 1,
        ),

        # ── Reduce LR on plateau ────────────────────────────
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor   = "val_loss",
            factor    = REDUCE_LR_FACTOR,
            patience  = REDUCE_LR_PATIENCE,
            min_lr    = MIN_LR,
            verbose   = 1,
            mode      = "min",
        ),

        # ── Early stopping ───────────────────────────────────
        tf.keras.callbacks.EarlyStopping(
            monitor              = monitor,
            patience             = EARLY_STOP_PATIENCE,
            restore_best_weights = True,
            verbose              = 1,
            mode                 = "max",
        ),

        # ── TensorBoard ──────────────────────────────────────
        tf.keras.callbacks.TensorBoard(
            log_dir          = os.path.join(LOG_DIR, phase),
            histogram_freq   = 1,
            write_graph      = False,
            update_freq      = "epoch",
        ),

        # ── CSV logging ──────────────────────────────────────
        tf.keras.callbacks.CSVLogger(
            filename = os.path.join(LOG_DIR, f"training_{phase}.csv"),
            append   = False,
        ),
    ]

    return callbacks

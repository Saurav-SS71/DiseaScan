"""
DISEASCAN — Evaluation Script
Run:
    python evaluate.py
"""

import os
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

from config   import VAL_DIR, MODEL_DIR, LOG_DIR, CLASSES, IMG_SIZE, TTA_STEPS, SEED
from data_pipeline import build_dataset

tf.random.set_seed(SEED)
np.random.seed(SEED)


# ─────────────────────────────────────────────
#  TEST-TIME AUGMENTATION
#  At inference we run N stochastic forward passes
#  with mild augmentation and average the softmax
#  outputs. This consistently gains +0.5–1.5% on
#  medical imaging benchmarks at no training cost.
# ─────────────────────────────────────────────

def _tta_transform(image):
    """Single stochastic augmentation for TTA."""
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_flip_up_down(image)
    image = tf.image.random_brightness(image, max_delta=0.10)
    image = tf.image.random_contrast(image, lower=0.90, upper=1.10)
    image = tf.clip_by_value(image, 0.0, 255.0)
    return image


def predict_with_tta(model, dataset, n_steps: int = TTA_STEPS):
    """
    For each batch, run n_steps augmented forward passes
    and return the mean prediction + original labels.
    """
    all_preds  = []
    all_labels = []

    print(f"\nRunning TTA with {n_steps} steps...")
    for images, labels in dataset:
        batch_preds = np.zeros((images.shape[0], len(CLASSES)), dtype=np.float32)

        for _ in range(n_steps):
            aug    = tf.map_fn(_tta_transform, images, dtype=tf.float32)
            preds  = model(aug, training=False).numpy()
            batch_preds += preds

        batch_preds /= n_steps
        all_preds.append(batch_preds)
        all_labels.append(labels.numpy())

    return np.vstack(all_preds), np.vstack(all_labels)


# ─────────────────────────────────────────────
#  METRICS
# ─────────────────────────────────────────────

def compute_metrics(y_true_oh, y_pred_proba):
    y_true = np.argmax(y_true_oh, axis=1)
    y_pred = np.argmax(y_pred_proba, axis=1)

    print("\n" + "=" * 60)
    print("  CLASSIFICATION REPORT")
    print("=" * 60)
    print(classification_report(y_true, y_pred, target_names=CLASSES, digits=4))

    # Per-class AUC (one-vs-rest)
    try:
        auc = roc_auc_score(y_true_oh, y_pred_proba, multi_class="ovr", average=None)
        print("Per-class AUC (OvR):")
        for cls, score in zip(CLASSES, auc):
            print(f"  {cls:<10}: {score:.4f}")
        print(f"  {'Macro avg':<10}: {np.mean(auc):.4f}")
    except Exception as e:
        print(f"AUC computation skipped: {e}")

    return y_true, y_pred


def plot_confusion_matrix(y_true, y_pred, save_path: str):
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)

    fig, axes = plt.subplots(1, 2, figsize=(20, 8))

    # Raw counts
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=CLASSES, yticklabels=CLASSES, ax=axes[0]
    )
    axes[0].set_title("Confusion Matrix — Raw Counts", fontsize=14)
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("True")

    # Normalised (recall per class on diagonal)
    sns.heatmap(
        cm_norm, annot=True, fmt=".2f", cmap="Blues",
        xticklabels=CLASSES, yticklabels=CLASSES, ax=axes[1]
    )
    axes[1].set_title("Confusion Matrix — Normalised (Recall)", fontsize=14)
    axes[1].set_xlabel("Predicted")
    axes[1].set_ylabel("True")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"\n✅  Confusion matrix saved → {save_path}")
    plt.close()


def plot_per_class_metrics(y_true, y_pred, save_path: str):
    report = classification_report(
        y_true, y_pred, target_names=CLASSES, output_dict=True
    )
    metrics_names = ["precision", "recall", "f1-score"]
    data = {m: [report[c][m] for c in CLASSES] for m in metrics_names}

    x      = np.arange(len(CLASSES))
    width  = 0.25
    fig, ax = plt.subplots(figsize=(14, 6))

    for i, (metric, values) in enumerate(data.items()):
        ax.bar(x + i * width, values, width, label=metric.capitalize())

    ax.set_xticks(x + width)
    ax.set_xticklabels(CLASSES, rotation=15)
    ax.set_ylim(0, 1.05)
    ax.set_title("Per-Class Precision / Recall / F1", fontsize=14)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"✅  Per-class metrics chart saved → {save_path}")
    plt.close()


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    model_path = os.path.join(MODEL_DIR, "diseascan_final.keras")
    print(f"\nLoading model: {model_path}")
    model = tf.keras.models.load_model(
        model_path,
        compile=False,
    )

    val_ds = build_dataset(VAL_DIR, training=False)

    # ── Standard evaluation ──────────────────
    print("\nRunning standard evaluation...")
    y_pred_proba, y_true_oh = predict_with_tta(model, val_ds, n_steps=1)
    y_true_std, y_pred_std  = compute_metrics(y_true_oh, y_pred_proba)

    # ── TTA evaluation ───────────────────────
    print("\nRunning TTA evaluation...")
    y_pred_tta, y_true_oh  = predict_with_tta(model, val_ds, n_steps=TTA_STEPS)
    y_true_tta, y_pred_tta_cls = compute_metrics(y_true_oh, y_pred_tta)

    # ── Plots ────────────────────────────────
    plot_confusion_matrix(
        y_true_tta, y_pred_tta_cls,
        save_path=os.path.join(LOG_DIR, "confusion_matrix_tta.png"),
    )
    plot_per_class_metrics(
        y_true_tta, y_pred_tta_cls,
        save_path=os.path.join(LOG_DIR, "per_class_metrics_tta.png"),
    )

    # ── Accuracy delta: standard vs TTA ──────
    acc_std = np.mean(y_true_std == y_pred_std)
    acc_tta = np.mean(y_true_tta == y_pred_tta_cls)
    print(f"\nStandard Accuracy : {acc_std:.4f}")
    print(f"TTA Accuracy      : {acc_tta:.4f}  (+{acc_tta - acc_std:.4f})")
    print("\n✅  Evaluation complete.\n")


if __name__ == "__main__":
    main()

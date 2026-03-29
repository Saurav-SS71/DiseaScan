import tensorflow as tf
from tensorflow.keras import losses, metrics
from config import NUM_CLASSES, LABEL_SMOOTHING, CLASSES


# ─────────────────────────────────────────────
#  FOCAL LOSS
#  Better than plain cross-entropy when a subset
#  of classes are still "harder" even after balancing.
#  gamma=2 is the standard; alpha uniform since
#  dataset is now roughly balanced.
# ─────────────────────────────────────────────

@tf.keras.utils.register_keras_serializable(package="DISEASCAN")
class FocalLoss(tf.keras.losses.Loss):
    def __init__(self, gamma: float = 2.0, label_smoothing: float = 0.10, **kwargs):
        super().__init__(**kwargs)
        self.gamma           = gamma
        self.label_smoothing = label_smoothing

    def call(self, y_true, y_pred):
        # Apply label smoothing manually
        n_classes  = tf.cast(tf.shape(y_true)[-1], tf.float32)
        y_true_sm  = y_true * (1.0 - self.label_smoothing) + (self.label_smoothing / n_classes)

        y_pred     = tf.clip_by_value(y_pred, 1e-7, 1.0 - 1e-7)
        ce          = -y_true_sm * tf.math.log(y_pred)
        focal_w    = tf.pow(1.0 - y_pred, self.gamma)
        focal_loss = focal_w * ce
        return tf.reduce_mean(tf.reduce_sum(focal_loss, axis=-1))

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"gamma": self.gamma, "label_smoothing": self.label_smoothing})
        return cfg


def get_loss():
    """
    Focal loss preferred over plain CCE here because:
    - Even after balancing, vasc/df are visually distinct
      and their samples may still be harder to learn.
    - gamma=2 down-weights easy samples, pushing the model
      to focus on boundary cases.
    - label_smoothing prevents over-confident softmax outputs,
      which is critical for calibrated medical predictions.
    """
    return FocalLoss(gamma=2.0, label_smoothing=LABEL_SMOOTHING, name="focal_loss")


# ─────────────────────────────────────────────
#  METRICS
# ─────────────────────────────────────────────

def get_metrics():
    return [
        metrics.CategoricalAccuracy(name="accuracy"),
        metrics.Precision(name="precision"),
        metrics.Recall(name="recall"),
        metrics.AUC(name="auc", multi_label=False),
    ]


# ─────────────────────────────────────────────
#  CLASS WEIGHTS
#  Dataset is semi-balanced but melanoma/nevus are
#  2.5× larger than df/vasc. We apply mild weighting
#  as a safety net — not to compensate imbalance
#  dramatically but to signal relative importance.
# ─────────────────────────────────────────────

def compute_class_weights(class_counts: dict) -> dict:
    total  = sum(class_counts.values())
    n_cls  = len(class_counts)
    # sklearn-style balanced weighting
    weights = {}
    for idx, cls in enumerate(CLASSES):
        weights[idx] = total / (n_cls * class_counts[cls])
    return weights

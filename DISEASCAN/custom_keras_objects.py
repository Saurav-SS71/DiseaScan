"""
Custom Keras classes and functions for DISEASCAN.
This module is designed to be safely imported externally.
"""

import tensorflow as tf
import numpy as np


@tf.keras.utils.register_keras_serializable()
class WarmupCosineDecay(tf.keras.optimizers.schedules.LearningRateSchedule):
    """Linear warm-up followed by cosine decay learning rate schedule."""
    
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


@tf.keras.utils.register_keras_serializable()
class FocalLoss(tf.keras.losses.Loss):
    """Focal Loss for handling class imbalance and hard examples."""
    
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

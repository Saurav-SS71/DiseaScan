import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import EfficientNetB4
from config import IMG_SIZE, CHANNELS, NUM_CLASSES, DROPOUT_RATE


def build_model(trainable_base: bool = False) -> Model:
    """
    EfficientNetB4 + custom classification head.

    Phase 1: base frozen  — train head only
    Phase 2: base partial — fine-tune top layers

    EfficientNetB4 input: [0, 255] float32
    Its internal preprocess_input does rescaling/normalisation.
    """
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, CHANNELS), name="input_image")

    # ── Base model ───────────────────────────────────────────
    base = EfficientNetB4(
        include_top=False,
        weights="imagenet",
        input_tensor=inputs,
        name="efficientnetb4",
    )
    base.trainable = trainable_base

    # ── Head ─────────────────────────────────────────────────
    x = base.output

    # Global average pooling instead of flatten — fewer params,
    # better spatial generalisation for dermoscopic images
    x = layers.GlobalAveragePooling2D(name="gap")(x)

    # Dense block 1
    x = layers.Dense(512, name="dense_1")(x)
    x = layers.BatchNormalization(name="bn_1")(x)
    x = layers.Activation("relu", name="relu_1")(x)
    x = layers.Dropout(DROPOUT_RATE, name="drop_1")(x)

    # Dense block 2
    x = layers.Dense(256, name="dense_2")(x)
    x = layers.BatchNormalization(name="bn_2")(x)
    x = layers.Activation("relu", name="relu_2")(x)
    x = layers.Dropout(DROPOUT_RATE * 0.75, name="drop_2")(x)

    # Output
    outputs = layers.Dense(NUM_CLASSES, activation="softmax", name="predictions")(x)

    model = Model(inputs=inputs, outputs=outputs, name="DISEASCAN_EfficientNetB4")
    return model


def unfreeze_top_layers(model: Model, from_layer: int = -60) -> Model:
    """
    Selectively unfreeze the top N layers of the base for fine-tuning.
    BatchNorm layers stay frozen to prevent distribution shift.
    
    Works both for freshly built models and deserialized ones where the 
    EfficientNet base is flattened into individual layers.
    """
    # Try to find and unfreeze the named base (fresh model)
    try:
        base = model.get_layer("efficientnetb4")
        base.trainable = True
        for layer in base.layers[:from_layer]:
            layer.trainable = False
    except ValueError:
        # If the base isn't a named layer, we're working with a deserialized model.
        # Unfreeze the last N layers of the entire model instead.
        for layer in model.layers[:from_layer]:
            layer.trainable = False

    # Keep ALL BatchNorm layers frozen during fine-tuning —
    # critical to prevent ImageNet BN stats from corrupting
    for layer in model.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False

    return model


def model_summary(model: Model):
    model.summary(line_length=100)
    trainable     = sum(tf.size(w).numpy() for w in model.trainable_weights)
    non_trainable = sum(tf.size(w).numpy() for w in model.non_trainable_weights)
    print(f"\nTrainable params    : {trainable:,}")
    print(f"Non-trainable params: {non_trainable:,}")

import tensorflow as tf
from config import (
    TRAIN_DIR, VAL_DIR, IMG_SIZE, BATCH_SIZE,
    NUM_CLASSES, SEED
)

AUTOTUNE = tf.data.AUTOTUNE

# ─────────────────────────────────────────────
#  NORMALISATION
#  EfficientNet expects [0, 255] — its own
#  preprocess_input handles scaling internally.
#  We keep raw uint8 here and apply inside model.
# ─────────────────────────────────────────────

def _decode_and_resize(path, label):
    raw   = tf.io.read_file(path)
    image = tf.image.decode_jpeg(raw, channels=3)
    image = tf.image.resize(image, [IMG_SIZE, IMG_SIZE])
    image = tf.cast(image, tf.float32)
    return image, label


def _augment_train(image, label):
    """
    Runtime augmentation kept light — heavy augmentation
    was already applied offline. This adds cheap diversity
    without re-augmenting aggressively.
    """
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_flip_up_down(image)
    image = tf.image.random_brightness(image, max_delta=0.15)
    image = tf.image.random_contrast(image, lower=0.85, upper=1.15)
    image = tf.image.random_saturation(image, lower=0.85, upper=1.15)
    image = tf.clip_by_value(image, 0.0, 255.0)
    return image, label


def _one_hot(image, label):
    label = tf.one_hot(label, NUM_CLASSES)
    return image, label


def build_dataset(directory: str, training: bool) -> tf.data.Dataset:
    ds = tf.keras.utils.image_dataset_from_directory(
        directory,
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=None,           # unbatched — we batch after augmentation
        label_mode="int",
        shuffle=training,
        seed=SEED,
        interpolation="bilinear",
    )

    # one-hot encode
    ds = ds.map(_one_hot, num_parallel_calls=AUTOTUNE)

    if training:
        ds = ds.map(_augment_train, num_parallel_calls=AUTOTUNE)
        ds = ds.shuffle(buffer_size=2048, seed=SEED)

    ds = (
        ds
        .batch(BATCH_SIZE, drop_remainder=training)
        .cache("dataset_cache")
        .prefetch(AUTOTUNE)
    )
    return ds


def get_datasets():
    train_ds = build_dataset(TRAIN_DIR, training=True)
    val_ds   = build_dataset(VAL_DIR,   training=False)
    return train_ds, val_ds

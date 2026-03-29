import os

# ─────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────
TRAIN_DIR = "train"
VAL_DIR   = "val"
MODEL_DIR   = "models"
LOG_DIR     = "logs"

# ─────────────────────────────────────────────
#  CLASSES
# ─────────────────────────────────────────────
CLASSES = ["akiec", "bcc", "bkl", "df", "melanoma", "nevus", "vasc"]
NUM_CLASSES = len(CLASSES)

CLASS_COUNTS = {
    "akiec":   6000,
    "bcc":     7000,
    "bkl":     6000,
    "df":      5000,
    "melanoma":14000,
    "nevus":   14000,
    "vasc":    5000,
}
TOTAL_TRAIN = sum(CLASS_COUNTS.values())  # 57000

# ─────────────────────────────────────────────
#  IMAGE
# ─────────────────────────────────────────────
IMG_SIZE    = 380
CHANNELS    = 3

# ─────────────────────────────────────────────
#  TRAINING — PHASE 1 (head only)
# ─────────────────────────────────────────────
BATCH_SIZE      = 8
EPOCHS_HEAD     = 15
LR_HEAD         = 1e-3

# ─────────────────────────────────────────────
#  TRAINING — PHASE 2 (fine-tune)
# ─────────────────────────────────────────────
EPOCHS_FINETUNE     = 20
LR_FINETUNE         = 5e-5
UNFREEZE_FROM_LAYER = -60          # unfreeze last 60 layers of EfficientNet

# ─────────────────────────────────────────────
#  REGULARISATION
# ─────────────────────────────────────────────
DROPOUT_RATE    = 0.40
LABEL_SMOOTHING = 0.10

# ─────────────────────────────────────────────
#  CALLBACKS
# ─────────────────────────────────────────────
EARLY_STOP_PATIENCE = 10
REDUCE_LR_PATIENCE  = 4
REDUCE_LR_FACTOR    = 0.3
MIN_LR              = 1e-7

# ─────────────────────────────────────────────
#  MISC
# ─────────────────────────────────────────────
SEED        = 42
TTA_STEPS   = 8

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR,   exist_ok=True)

import tensorflow as tf
import sys
import os

# Add DISEASCAN path to import custom classes
diseascan_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../DISEASCAN'))
if diseascan_path not in sys.path:
    sys.path.insert(0, diseascan_path)

# Import custom classes to register them with Keras before loading the model
from custom_keras_objects import WarmupCosineDecay, FocalLoss

MODEL_PATH = "app/models/diseascan_finetune_best.keras"

# Load model with explicit custom_objects mapping (for compatibility)
try:
    model = tf.keras.models.load_model(
        MODEL_PATH,
        custom_objects={
            'WarmupCosineDecay': WarmupCosineDecay,
            'FocalLoss': FocalLoss,
        }
    )
except Exception as e:
    print(f"Error loading model: {e}")
    raise

# Class labels (EDIT THIS based on your dataset)
CLASS_NAMES = [
    "akiec",   # Actinic keratoses
    "bcc",     # Basal cell carcinoma
    "bkl",     # Benign keratosis
    "df",      # Dermatofibroma
    "mel",     # Melanoma
    "nv",      # Nevus
    "vasc"     # Vascular lesions
]

def predict(image_array):
    preds = model.predict(image_array)
    
    predicted_index = preds.argmax(axis=1)[0]
    confidence = float(preds[0][predicted_index])
    
    return CLASS_NAMES[predicted_index], confidence
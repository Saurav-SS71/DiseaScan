from PIL import Image
import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input

def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((380, 380))

    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)

    # IMPORTANT
    img_array = preprocess_input(img_array)

    return img_array
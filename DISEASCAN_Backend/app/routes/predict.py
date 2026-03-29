from fastapi import APIRouter, UploadFile, File
import os
from uuid import uuid4

from app.utils.image_utils import preprocess_image
from app.models.model_loader import predict

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):

    if not file.content_type.startswith("image/"):
        return {"error": "File must be an image"}

    # Save image
    filename = f"{uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Preprocess
    image_array = preprocess_image(file_path)

    # Predict
    prediction, confidence = predict(image_array)

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "image_path": file_path
    }
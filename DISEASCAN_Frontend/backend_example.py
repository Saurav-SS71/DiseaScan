"""
Example FastAPI Backend for DiseaScan
This is a reference implementation showing how to set up the backend API.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List

app = FastAPI(title="DiseaScan API")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Prediction(BaseModel):
    label: str
    confidence: float


class PredictionResponse(BaseModel):
    predictions: List[Prediction]


class ExplanationRequest(BaseModel):
    disease: str
    confidence: float


class ExplanationResponse(BaseModel):
    explanation: str


# Mock disease detection - replace with your ML model
def predict_disease_from_image(image_bytes: bytes) -> PredictionResponse:
    """
    Replace this with your actual ML model inference
    """
    # Example: Load your trained model here
    # model = load_model('disease_model.h5')
    # predictions = model.predict(processed_image)
    
    # Mock response for testing
    return PredictionResponse(
        predictions=[
            Prediction(label="Healthy Skin", confidence=0.7),
            Prediction(label="Eczema", confidence=0.2),
            Prediction(label="Psoriasis", confidence=0.1),
        ]
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Analyze image and return disease predictions
    
    Args:
        file: Image file to analyze
        
    Returns:
        PredictionResponse with top 3 disease predictions and confidence scores
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image file."
        )
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Run disease detection
        result = predict_disease_from_image(image_bytes)
        
        # Sort by confidence and return top 3
        result.predictions.sort(key=lambda x: x.confidence, reverse=True)
        result.predictions = result.predictions[:3]
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/explain", response_model=ExplanationResponse)
async def explain_disease(request: ExplanationRequest):
    """
    Generate explanation for detected disease
    
    To use OpenAI API:
    1. Install: pip install openai
    2. Set OPENAI_API_KEY environment variable
    3. Uncomment the OpenAI code below
    
    Args:
        request: ExplanationRequest containing disease name and confidence
        
    Returns:
        ExplanationResponse with AI-generated disease explanation
    """
    
    # Option 1: Use OpenAI (uncomment and configure)
    # from openai import OpenAI
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "You are a medical assistant. Provide concise explanations of skin diseases including symptoms, causes, and basic precautions."
    #         },
    #         {
    #             "role": "user",
    #             "content": f"Explain {request.disease} detected with {request.confidence*100:.1f}% confidence. Include symptoms, causes, and treatment options."
    #         }
    #     ]
    # )
    # explanation = response.choices[0].message.content
    
    # Option 2: Use predefined explanations (mock)
    mock_explanations = {
        "Healthy Skin": "This skin appears to be healthy. Continue maintaining good skincare practices with daily moisturizing, sun protection, and a balanced diet.",
        "Eczema": "Eczema is a chronic inflammatory condition causing intense itching and redness. Common triggers include irritants and allergens. Treatment includes regular moisturizing and topical corticosteroids.",
        "Psoriasis": "Psoriasis is an autoimmune condition causing red, scaly patches. Management includes topical treatments, phototherapy, and stress management.",
        "Acne": "Acne results from clogged pores and bacteria. Treatment options include topical retinoids, benzoyl peroxide, and in severe cases, oral medications.",
        "Melanoma": "This requires immediate professional medical attention. Melanoma is a serious form of skin cancer. Schedule a dermatology appointment urgently.",
    }
    
    explanation = mock_explanations.get(
        request.disease,
        f"Detected condition: {request.disease} with {request.confidence*100:.1f}% confidence. Please consult with a healthcare professional for proper diagnosis and treatment."
    )
    
    return ExplanationResponse(explanation=explanation)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "DiseaScan API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

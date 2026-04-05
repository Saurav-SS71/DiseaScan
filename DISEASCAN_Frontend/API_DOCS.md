# DiseaScan API Documentation

## Overview

DiseaScan is a disease detection system with a modern React frontend and FastAPI backend. This document covers the API integration, endpoints, and implementation details.

## Architecture

```
┌─────────────────────────┐
│   React Frontend (Vite) │
│                         │
│  - ChatGPT-like UI      │
│  - Image Upload         │
│  - Message History      │
└────────────┬────────────┘
             │ HTTP/HTTPS
             ▼
┌─────────────────────────┐
│   FastAPI Backend       │
│                         │
│  - Image Processing     │
│  - ML Model Inference   │
│  - LLM Integration      │
└─────────────────────────┘
```

## API Endpoints

### 1. Disease Prediction

**Endpoint:** `POST /predict`

**Purpose:** Analyze medical image and return top 3 disease predictions

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file` (File, required): Medical image (PNG, JPG, GIF)

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@patient_skin.jpg"
```

**Example (JavaScript/Axios):**
```typescript
const formData = new FormData()
formData.append('file', imageFile)

const response = await axios.post(
  'http://localhost:8000/predict',
  formData,
  {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }
)
```

**Response (200 OK):**
```json
{
  "predictions": [
    {
      "label": "Melanoma",
      "confidence": 0.92
    },
    {
      "label": "Nevus",
      "confidence": 0.07
    },
    {
      "label": "Basal Cell Carcinoma",
      "confidence": 0.01
    }
  ]
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid file type. Please upload an image file."
}
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Error processing image: [error message]"
}
```

**Validation Rules:**
- File type must be: `image/jpeg`, `image/png`, or `image/gif`
- File size should be < 10MB (recommended)
- Image resolution: 224x224 to 2048x2048 (depends on model)

---

### 2. Disease Explanation

**Endpoint:** `POST /explain`

**Purpose:** Generate detailed explanation for detected disease

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "disease": "string",
    "confidence": "number (0-1)"
  }
  ```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"disease": "Melanoma", "confidence": 0.92}'
```

**Example (JavaScript/Axios):**
```typescript
const response = await axios.post(
  'http://localhost:8000/explain',
  {
    disease: 'Melanoma',
    confidence: 0.92,
  }
)
```

**Response (200 OK):**
```json
{
  "explanation": "Melanoma is the most serious type of skin cancer, originating from melanocytes (pigment-producing cells). With 92% confidence, the analyzed image shows characteristics consistent with melanoma. Key features typically include irregular borders, asymmetry, and varied color distribution. Early detection significantly improves treatment outcomes. This requires immediate professional medical evaluation and possibly biopsy confirmation. Treatment options may include surgical excision, immunotherapy, or targeted therapy depending on stage and individual factors."
}
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Error generating explanation: [error message]"
}
```

**Parameters:**
- `disease` (string): Name of detected disease
- `confidence` (number): Confidence score (0.0 to 1.0)

---

### 3. Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify API is running and healthy

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "DiseaScan API"
}
```

---

## Error Handling

### Standard Error Format

All errors follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

### Common Error Codes

| Code | Reason | Solution |
|------|--------|----------|
| 400 | Invalid file type | Ensure file is PNG, JPG, or GIF |
| 400 | File too large | Compress image to < 10MB |
| 422 | Invalid JSON | Check request body format |
| 500 | Processing error | Check backend logs |
| 503 | Service unavailable | Backend server is down |

---

## Request/Response Examples

### Complete Chat Flow

**1. User uploads image:**
```javascript
// Frontend: Prepare image
const imageFile = /* File from input */
const formData = new FormData()
formData.append('file', imageFile)

// Send to backend
const predictions = await axios.post('/predict', formData)
// Response: { predictions: [...] }
```

**2. Get disease explanation:**
```javascript
// Frontend: Request explanation
const topDisease = predictions.predictions[0]
const explanation = await axios.post('/explain', {
  disease: topDisease.label,
  confidence: topDisease.confidence,
})
// Response: { explanation: "..." }
```

**3. Display to user:**
```javascript
// Frontend: Show predictions and explanation
// Predictions table with confidence percentages
// AI-generated explanation text
```

---

## Backend Implementation

### Using the Example Backend

The provided `backend_example.py` includes:

1. **Flask/FastAPI setup** with CORS enabled
2. **Mock predictions** for testing (replace with your model)
3. **Mock explanations** as fallback (replace with OpenAI/LLM)
4. **Error handling** and input validation

### Replacing Mock Predictions

**Step 1:** Import your ML model
```python
from your_module import DiseaseDetectionModel
model = DiseaseDetectionModel.load('model.h5')
```

**Step 2:** Update predict_disease_from_image function
```python
def predict_disease_from_image(image_bytes: bytes):
    # Process image
    image = process_image(image_bytes)
    
    # Get predictions from model
    predictions = model.predict(image)
    
    # Return formatted response
    return PredictionResponse(predictions=predictions)
```

### Adding OpenAI Integration

**Step 1:** Install package
```bash
pip install openai
```

**Step 2:** Set environment variable
```bash
export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

**Step 3:** Update explain endpoint
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/explain")
async def explain_disease(request: ExplanationRequest):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a dermatology assistant..."
            },
            {
                "role": "user",
                "content": f"Explain {request.disease} with {request.confidence*100:.1f}% confidence"
            }
        ]
    )
    return ExplanationResponse(
        explanation=response.choices[0].message.content
    )
```

---

## Rate Limiting

For production, implement rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/predict")
@limiter.limit("10/minute")
async def predict(request: Request, file: UploadFile):
    # Implementation
```

---

## Authentication (Optional)

Add JWT authentication for security:

```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthCredentials):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401)

@app.post("/predict")
async def predict(
    credentials: HTTPAuthCredentials = Depends(security),
    file: UploadFile = File(...)
):
    user = verify_token(credentials)
    # Process image
```

---

## Testing the API

### Using Postman

1. Create POST request to `http://localhost:8000/predict`
2. Set Body → form-data
3. Add key `file` with type `File`
4. Select your test image
5. Send request

### Using Python

```python
import requests

# Test prediction
with open('test_image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/predict',
        files=files
    )
    print(response.json())

# Test explanation
response = requests.post(
    'http://localhost:8000/explain',
    json={'disease': 'Melanoma', 'confidence': 0.92}
)
print(response.json())
```

### Using JavaScript/Fetch

```javascript
// Test prediction
const formData = new FormData()
formData.append('file', imageFile)

const response = await fetch(
  'http://localhost:8000/predict',
  { method: 'POST', body: formData }
)
console.log(await response.json())

// Test explanation
const response = await fetch(
  'http://localhost:8000/explain',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      disease: 'Melanoma',
      confidence: 0.92,
    }),
  }
)
console.log(await response.json())
```

---

## CORS Configuration

The backend has CORS enabled for development. For production, restrict origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Performance Optimization

### Image Processing
- Compress images before upload
- Use appropriate image dimensions for your model
- Implement client-side validation

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_disease_info(disease: str):
    # Cache disease information
    return disease_database.get(disease)
```

### Async Processing
```python
from celery import Celery

celery_app = Celery('diseascan')

@celery_app.task
def process_image(image_path):
    # Long-running task
    predictions = model.predict(image_path)
    return predictions
```

---

## Deployment

### Environment Variables

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxx
MODEL_PATH=/models/disease_model.h5
UPLOAD_FOLDER=/tmp/uploads
PYTHONUNBUFFERED=1
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "backend_example:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Monitoring & Logging

Add logging to track API usage:

```python
import logging

logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(file: UploadFile):
    logger.info(f"Prediction request for file: {file.filename}")
    try:
        result = predict_disease_from_image(await file.read())
        logger.info(f"Prediction successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise
```

---

## Support & Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify dependencies
pip install -r requirements.txt

# Run with debug
uvicorn backend_example:app --reload
```

### CORS errors in browser
- Ensure backend has CORS middleware configured
- Check frontend API URL matches backend origin
- Verify backend is running

### Slow predictions
- Profile your model: `cProfile`
- Consider using GPU acceleration
- Implement prediction caching
- Use model quantization

---

## Version History

- **v1.0** (Current): Initial release with basic prediction and explanation endpoints
- **v1.1** (Planned): Authentication, rate limiting, logging
- **v2.0** (Planned): Async task processing, advanced analytics

---

## License

MIT - Use freely for educational and commercial purposes

from fastapi import FastAPI
from app.routes import predict

app = FastAPI()

@app.get("/")
def home():
    return{"message" : "Working"}

@app.get("/test")
def test():
    return {"status": "working"}

app.include_router(predict.router)

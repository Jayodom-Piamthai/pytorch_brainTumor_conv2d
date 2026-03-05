# run with : uvicorn webAPI:app --reload
# swagger docs at : [url]/docs
from fastapi import FastAPI,status,File,UploadFile,HTTPException
from typing import Annotated
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import time
from contextlib import asynccontextmanager

from torchvision import datasets, transforms
import torch
from PIL import Image

image_height = 224
image_width = 224
scannerPreprocess = transforms.Compose([
    transforms.Resize((image_height,image_width)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

app = FastAPI()

#-----------------MIDDLEWARE---------------------
origins = [
    "https://localhost",    
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



MODEL_PATH = "./BrainTumorModel.pth"
LABELS = {}
model_loading_time = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODEL_PATH, LABELS, model_loading_time
    # Load model on startup
    model_loading_start_time = time.time()
    app.state.model = torch.load(MODEL_PATH)
    app.state.model.eval()
    # Load Labels
    with open("imagenet_class_index.json", "r") as f:
        LABELS = json.load(f)
    model_loading_time = time.time() - model_loading_start_time
    yield
    # Clean up resources on shutdown
    del app.state.model

# app = FastAPI(lifespan=lifespan, title="Pytorch API")

app = FastAPI(title =' Brain Tumor Scan API')

@app.get("/", status_code=status.HTTP_200_OK)
async def test():
    return {"message": "Hello World"}   

@app.get("/model", status_code=status.HTTP_200_OK)
def model_info():
    return f"Model loaded in {model_loading_time} s"

@app.get('model/predict/')
async def upload_image(file: UploadFile = File(...)):
    # Optional: Validate content type (MIME type)
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or GIF images are allowed.")

@app.post("/predict")
async def tumor_prediction(file: UploadFile = File(...)):
    start_time = time.time()
    # Read and preprocess the image
    image = Image.open(file.file).convert("RGB")
    input_data = scannerPreprocess(image)

    # # Run inference
    # with torch.no_grad():
    #     results = app.state.model(input_data)

    # # Get the predicted class probabilities
    # # probabilities = torch.nn.functional.softmax(results[0], dim=0)
    # # top_prob, top_class = torch.max(probabilities, 0)
    # # label = LABELS[str(top_class.item())][-1]
    # # score = top_prob.item()

    # inference_time = time.time() - start_time

    return input_data
    
    # return {
    #     "class": label,
    #     "score": score,
    #     "inference_time (s)": inference_time,
    #     "model_loading_time (s)": model_loading_time,
    # }

@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}
    return {"filename": file.file}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.file}
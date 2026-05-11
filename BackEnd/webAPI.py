# run with : uvicorn webAPI:app --reload
# swagger docs at : [url]/docs
from fastapi import FastAPI,status,File,UploadFile,HTTPException
from typing import Annotated
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import time
from contextlib import asynccontextmanager

from predictionSchema import PredictionRequest, PredictionResponse

from torchvision import datasets, transforms
from torch import torch,nn,optim
from PIL import Image

#----------------Model define-------------------------------
image_height = 224
image_width = 224
scannerPreprocess = transforms.Compose([
    transforms.Resize((image_height,image_width)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

class CNN_tumor(nn.Module):
    def __init__(self, model_path: str):
        super().__init__()
        """
        Initialize the model by loading the pre-trained model from the specified path.
        """
        # self.model
        
        # Load the trained model (assuming it's a PyTorch model saved as .pth)
        self.model = torch.load(model_path)
        self.model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
        # self.model.eval()  # Set the model to evaluation mode

def predict(brainScanImage):
    model.eval()
    with torch.no_grad():
        input_data = scannerPreprocess(brainScanImage).to(device)
        y_preds = model(input_data.unsqueeze(0))
        predicted_class = torch.argmax(y_preds, dim=1).item()
        print(f"tumor prediction : class {predicted_class} ; {y_preds}")

#--------------FastAPI----------------------
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

#---------------------api title------------------------------
app = FastAPI(title =' Brain Tumor Scan API')
#--------------------model holder----------------------
model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# -------------------api requests-------------------------
    
@app.get("/", status_code=status.HTTP_200_OK)
async def test():
    return {"message": "Hello World"}   

@app.get('/modelTest')
async def model_func_test():
    model = CNN_tumor(MODEL_PATH).to(device)
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
    # model.load_state_dict(torch.load("model_weights.pth", map_location=device)) # Load your weights
    model.to(device)
    model.eval() # Set model to evaluation mode
    return{"Model loaded and ready!"}

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
    # model = CNN_tumor()
    # # Run inference
    # with torch.no_grad():
    #     results = app.state.model(input_data)

    # # Get the predicted class probabilities
    # # probabilities = torch.nn.functional.softmax(results[0], dim=0)
    # # top_prob, top_class = torch.max(probabilities, 0)
    # # label = LABELS[str(top_class.item())][-1]
    # # score = top_prob.item()

    # inference_time = time.time() - start_time

    return {"img_data" :input_data ,
            # "model data" : model,
            }
    # return image
    
    # return {
    #     "class": label,
    #     "score": score,
    #     "inference_time (s)": inference_time,
    #     "model_loading_time (s)": model_loading_time,
    # }

@app.post("/files/")
async def test_file_data_get(file: UploadFile):
    return {"file_name": file.filename,
            "file_size": file.content_type,
            # "file": file.file
            
            }
    # return {"filename": file.filename}

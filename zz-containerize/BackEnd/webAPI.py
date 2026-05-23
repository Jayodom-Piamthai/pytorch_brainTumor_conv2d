# run with : uvicorn webAPI:app --reload
# swagger docs at : [url]/docs

#---------------------------fast api------------------------------
from fastapi import FastAPI,status,File,UploadFile,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import time
from contextlib import asynccontextmanager

#--------------------torch and image operations-------------------
import torch
from torchvision import datasets, transforms
from torchvision.transforms import Compose, ColorJitter, ToTensor
from PIL import Image

#----------------Model define + helper functions-------------------------------
from ConvModel import CNN_tumor
import io
image_height = 224
image_width = 224
scannerPreprocess = transforms.Compose([
    transforms.Resize((image_height,image_width)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

async def file_to_image(file):
    image = await file.read() #turn image file into raw bytes so Image can process it
    image = Image.open(io.BytesIO(image)).convert("RGB")
    image = scannerPreprocess(image).to(device).unsqueeze(0)
    return image

PATH  = "BrainTumorModel.pth" #name of pretrained model file
def prediction(brainScanImage):
    model.eval()
    with torch.no_grad():
        y_preds = model(brainScanImage)
        predicted_class = torch.argmax(y_preds, dim=1).item()
        return(f"tumor prediction : class {'yes' if predicted_class== 1 else 'no'} ; {y_preds}")


#---------------------async context-------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)
    model = CNN_tumor(in_channels=3).to(device)
    model.load_state_dict(torch.load("BrainTumorModel.pth", weights_only=True,map_location=device))
    model.eval()
    print("Model loaded!")
    yield
    # cleanup on shutdown (if needed)
    print("Shutting down...")

#---------------------api init------------------------------

app = FastAPI(lifespan=lifespan,title =' Brain Tumor Scan API')

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

model_loading_time = 0

#--------------------model holder----------------------

model = None # this will be replace with CNN_Tumor when api starts up
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# -------------------api requests-------------------------
    
@app.get("/", status_code=status.HTTP_200_OK)
async def test():
    return {"message": "Brain scan tumor API up and running"}   

@app.get('/model/test')
async def model_func_test():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CNN_tumor(in_channels=3,).to(device)
    model.load_state_dict(torch.load(PATH, weights_only=True))
    model.eval()
    return{"Model loaded and ready!"}

@app.post("/model/prediction")
async def predict_from_image_file(file: UploadFile = File(...)): #file is requested with key named "file" , in front we need to match this name
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or GIF images are allowed.")
    tumorImg = Image.open("TumorTestImage.jpg").convert('RGB')
    result = await file_to_image(file)
    print(type(result))
    # return ('image read')
    return prediction(result)

@app.post("/file_info/")
async def test_file_data_get(file: UploadFile):
    tumorImg = Image.open("TumorTestImage.jpg").convert('RGB')
    return {"file_name": file.filename,
            "file_type": file.content_type,
            # "image_type": type(tumorImg),
            # "file": file.file
            
            }
    # return {"filename": file.filename}
    


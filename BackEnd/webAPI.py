# run with : uvicorn webAPI:app --reload
# swagger docs at : [url]/docs

#---------------------------fast api------------------------------
from fastapi import FastAPI,status,File,UploadFile,HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import time
from contextlib import asynccontextmanager

#--------------------torch and image operations-------------------
import torch
from torchvision import datasets, transforms
from torchvision.transforms import Compose, ColorJitter, ToTensor
from PIL import Image

#----------------Model import + extra lib -------------------------------
from ConvModel import CNN_tumor
from ultralytics import YOLO
import io
import seaborn


#---------------------async context-------------------------

# creates a context that lets you allocate resources before running asynchronous code and release them after
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model , YOLO_ClassModel , YOLO_DetectModel , device , PATH , PATH_YOLO , PATH_YOLO_CLS
    
    PATH  = "Models/BrainTumorModelWeight.pth" #name of pretrained weight file
    PATH_YOLO = "Models/YOLO_TumorDetectWeight.pt"
    PATH_YOLO_CLS = "Models/YOLO_TumorClassWeight.pt"
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    YOLOdevice = '0' if torch.cuda.is_available() else 'cpu' #device 0 for ID
    model = CNN_tumor(in_channels=3).to(device)
    model.load_state_dict(torch.load(PATH, weights_only=True)) #path to CNN weight
    model.eval()
    YOLO_DetectModel = YOLO(PATH_YOLO) #path to YOLO weight 
    YOLO_DetectModel.eval() 
    YOLO_ClassModel = YOLO(PATH_YOLO_CLS) #path to YOLO weight 
    YOLO_ClassModel.eval()
    print("Model loaded!")
    yield
    # cleanup on shutdown (if needed)
    print("Shutting down...")

#--------------------model holder----------------------

# model = None # this will be replace with CNN_Tumor when api starts up

#----------------Model define + helper functions-------------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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

def prediction(brainScanImage):
    model.eval()
    with torch.no_grad():
        y_preds = model(brainScanImage)
        predicted_class = torch.argmax(y_preds, dim=1).item()
        return(f"tumor prediction : class {'yes' if predicted_class== 1 else 'no'} ; {y_preds}")

def YOLOprediction(brainScanImage):
    detResult = YOLO_DetectModel(brainScanImage)
    for result in detResult:
        resultImage = result
        boxes = result.boxes  # Boxes object for bounding box outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Probs object for classification outputs
        obb = result.obb  # Oriented boxes object for OBB outputs
        result.save(filename=f"./result/{brainScanImage.name}")
        result.show()
    clsResult = YOLO_ClassModel(brainScanImage)
    for result in clsResult:
        top1 = result.probs.top1  # top predicted class ID
        top1_conf = result.probs.top1conf  # top prediction confidence
        top1_name = result.names[top1]  # top predicted class name
        topResult = top1_name
        print(top1_name)
    fullResults = [topResult]
    # return(f"tumor prediction : class {predicted_class}")
    return(fullResults)
        
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
    RGBtumorImg = await file_to_image(file)
    print(type(RGBtumorImg))
    return prediction(RGBtumorImg)

@app.post("/model/YOLOprediction")
async def predict_from_image_file(file: UploadFile = File(...)): #file is requested with key named "file" , in front we need to match this name
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or GIF images are allowed.")
    tumorImg = Image.open("TumorTestImage.jpg").convert('RGB')
    RGBtumorImg = await file_to_image(file)
    print(type(RGBtumorImg))
    return YOLOprediction(RGBtumorImg)

@app.post("/file_info/")
async def test_file_data_get(file: UploadFile):
    tumorImg = Image.open("TumorTestImage.jpg").convert('RGB')
    return {"file_name": file.filename,
            "file_type": file.content_type,
            # "image_type": type(tumorImg),
            # "file": file.file
            
            }
    # return {"filename": file.filename}
    


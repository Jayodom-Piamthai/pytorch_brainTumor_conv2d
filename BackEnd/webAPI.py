# run with : uvicorn webAPI:app --reload
# swagger docs at : [url]/docs

#---------------------------fast api------------------------------
from fastapi import FastAPI,status,File,UploadFile,HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

#--------------------torch and image operations-------------------
import torch
from torchvision import datasets, transforms
from torchvision.transforms import Compose, ColorJitter, ToTensor
from PIL import Image

#----------------Model import + extra lib -------------------------------
from ConvModel import CNN_tumor
from ultralytics import YOLO
from io import BytesIO
from datetime import datetime
import io
import mimetypes
import json
import base64
import time
import os

#----------------vercel API-----------------------------------
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# from webAPI import app


#---------------------async context-------------------------

# creates a context that lets you allocate resources before running asynchronous code and release them after
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model , YOLO_ClassModel , YOLO_DetectModel , device , PATH , PATH_YOLO , PATH_YOLO_CLS
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    #path for model's weight files
    PATH = os.path.join(BASE_DIR, "Models/BrainTumorModelWeight.pth")
    PATH_YOLO = os.path.join(BASE_DIR, "Models/YOLO_TumorDetectWeight.pt")
    PATH_YOLO_CLS = os.path.join(BASE_DIR, "Models/YOLO_TumorClassWeight.pt")
    
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
    image = scannerPreprocess(image).to(device).unsqueeze(0) #preprocess image for detection
    return image

def prediction(brainScanImage):
    model.eval()
    with torch.no_grad():
        y_preds = model(brainScanImage)
        predicted_class = torch.argmax(y_preds, dim=1).item()
        return(f"tumor prediction : class {'yes' if predicted_class== 1 else 'no'} ; {y_preds}")


def imgEncode64(imagePath:str) -> str:
    with open(imagePath,'rb') as imgfile:
        print(type(imgfile))
        base64Encoded = base64.b64encode(imgfile.read()).decode('utf-8') #encode into utf8
        print(base64Encoded)
        print(type(base64Encoded))
        return(base64Encoded)
        # URL_IMG = f"data:image/png;base64,{base64Encoded}"
        # print(URL_IMG)

def imgToURI(inputImagePath:str) -> str:
    print(inputImagePath)
    imgMimetype = mimetypes.guess_type(inputImagePath)[0] or "image/png"
    print(imgMimetype)
    encodedImg = imgEncode64(inputImagePath)
    print(encodedImg)
    # return f"data:{imgMimetype};base64,{encodedImg}"   
    return encodedImg     

def imgDecode64(encodedStr:str):
    imgBytes = base64.b64decode(encodedStr)
    print(imgBytes)
    print(type(imgBytes))
    imgStream = io.BytesIO(imgBytes)
    Img = Image.open(imgStream)
    Img.show()

def YOLOprediction(brainScanImage):
    detResult = YOLO_DetectModel(brainScanImage)
    for result in detResult:
        resultImage = result
        boxes = result.boxes  # Boxes object for bounding box outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Probs object for classification outputs
        obb = result.obb  # Oriented boxes object for OBB outputs
        # img = Image.open(brainScanImage)
        # img.show()
        # image = np.squeeze(brainScanImage)
        # plt.imshow(image)
        # plt.show()
    clsResult = YOLO_ClassModel(brainScanImage)
    for result in clsResult:
        top1 = result.probs.top1  # top predicted class ID
        top1_conf = result.probs.top1conf  # top prediction confidence
        top1_name = result.names[top1]  # top predicted class name
        topResult = top1_name
        print(top1_name)
    fileName = f"./result/{top1_name}.png"
    resultImage.save(filename=fileName)
    encodedImage = imgEncode64(fileName)
    print(encodedImage)
    # resultImage.show()
    print(type(resultImage))
    print(f"./result/{datetime.now()}-{top1_name}.png")
    fullResults = {
        "detectionImage":encodedImage,
        "resultName":str(topResult),
    }
    # return(f"tumor prediction : class {predicted_class}")
    return(fullResults)


        
#---------------------api init------------------------------

app = FastAPI(lifespan=lifespan,title =' Brain Tumor Scan API')

#-----------------MIDDLEWARE---------------------


# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:5173"]

origins = ["*"]

frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    origins.append(frontend_url)

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
    RGBtumorImg = await file_to_image(file)
    print(type(RGBtumorImg))
    return prediction(RGBtumorImg)

@app.post("/model/YOLOprediction")
async def predict_from_image_file(file: UploadFile = File(...)): #file is requested with key named "file" , in front we need to match this name
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or GIF images are allowed.")
    tumorImg = Image.open("TumorTestImage.jpg").convert('RGB')
    image = await file.read() #turn image file into raw bytes so Image can process it
    image = Image.open(io.BytesIO(image)).convert("RGB")
    print(type(image))
    return YOLOprediction(image)

@app.post("/file_info/")
async def test_file_data_get(file: UploadFile):
    tumorImg = Image.open("TumorTestImage.jpg").convert('RGB')
    return {"file_name": file.filename,
            "file_type": file.content_type,
            # "image_type": type(tumorImg),
            # "file": file.file
            
            }
    # return {"filename": file.filename}
    


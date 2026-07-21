import torch
from ultralytics import YOLO

def main():
    # Model

    device = '0' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    # Load a pre-trained model (e.g., YOLOv11 nano or YOLOv8 nano)
    # model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=False)
    # model = YOLO("yolo11n.pt") #for bounding box modeling 
    model = YOLO("yolo11n-cls.pt")  #for classification - getting probs to be display in site

    # Begin training
    results = model.train(
        data="./YOLO_TumorDataset/data.yaml",   # Path to your dataset configx``
        epochs=100,                 # Total passes through dataset
        imgsz=640,                  # Image size resolution
        batch=16,                   # Training batch size
        device=device,              # GPU device ID or 'cpu'
        workers=4                   # Number of data loader CPU threads
    )
    
    # weight AFTER TRAIN will be stored in a folder runs/detect/train 


if __name__ == '__main__':
    main()
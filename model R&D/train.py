import os
import torch
from torch import nn , optim 
from torch.utils.data import DataLoader,Dataset,random_split
from torchinfo import summary
from torchvision import datasets, transforms
from torchvision.transforms import Compose, ColorJitter, ToTensor
from torchvision.io import decode_image
from torchvision.datasets import ImageFolder
from lightning.pytorch.callbacks.early_stopping import EarlyStopping
from lightning.pytorch import Trainer
from PIL import Image
from datasets import load_dataset
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ConvModel import CNN_tumor


batch_size = 16

image_height = 224
image_width = 224

preprocess = transforms.Compose([
    transforms.Resize((image_width,image_height)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    # transforms.ColorJitter(brightness=0.3,contrast=0.3,saturation=0.3),
    transforms.ToTensor(), # Converts PIL to [3, 32, 32] Tensor -> rgb size 32*32
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

valPreprocess = transforms.Compose([
    transforms.Resize((image_width,image_height)),
    transforms.RandomRotation(15),
    transforms.ToTensor(), # Converts PIL to [3, 32, 32] Tensor -> rgb size 32*32
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])



finalTestPreprocess = transforms.Compose([
    transforms.Resize((image_height,image_width)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

#ImageFolder automatically one hot folder(no as 0,yes as 1) so we dont have to put label ourselves
brain_dataset =ImageFolder(root='brain_tumor_dataset', transform=None)

#test train val split -> split now so dataloader and transformation can be done with no problem
train_size = round(0.7*len(brain_dataset)) #split wont take float,we need to round that up to int
val_size = round(0.15*len(brain_dataset))
test_size = len(brain_dataset) - train_size - val_size
train_dataset, val_dataset , test_dataset = random_split(
    brain_dataset,
    [train_size, val_size,test_size],
    generator=torch.Generator().manual_seed(42)
    )

#wrapper class,so we can do separate transformation and have test unchanged
class BrainTumorDataset(Dataset):
    def __init__(self, subset, transform=None):
        self.subset = subset
        self.transform = transform
        
    def __getitem__(self, index):
        x, y = self.subset[index]
        if self.transform:
            x = self.transform(x)
        return x, y
        
    def __len__(self):
        return len(self.subset)

train_dataset = BrainTumorDataset(subset=train_dataset, transform=preprocess)
val_dataset = BrainTumorDataset(subset=val_dataset, transform=valPreprocess)
test_dataset = BrainTumorDataset(subset=test_dataset, transform=finalTestPreprocess)

#put into dataloader for iterations in the model
train_loader = DataLoader(train_dataset,batch_size=batch_size,shuffle=True)
val_loader = DataLoader(val_dataset,batch_size=batch_size,shuffle=True)
test_loader = DataLoader(test_dataset,batch_size=batch_size,shuffle=False)

#get amount of output classes
classes_amount = len(brain_dataset.classes)
print(classes_amount)

image , label = next(iter(train_loader))
print(image,label)

#====================================model===============================================

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CNN_tumor(in_channels=3,out_classes=classes_amount).to(device)

# loss func set
criterion = nn.CrossEntropyLoss()
# adam optim , learning rate 0.001
optimizer = optim.Adam(model.parameters(), lr=0.001) 

print(model)
summary(model, input_size=(100,3,image_height,image_width))# (Batch Size, Channels, Height, Width)

#====================================training===============================================

epochs = 25

# For tracking progress
history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}

early_stop_callback = EarlyStopping(monitor="val_loss", min_delta=0.00, patience=3, verbose=False, mode="min")
trainer = Trainer(callbacks=[early_stop_callback])


for epoch in range(epochs):
    # --- TRAINING PHASE ---
    model.train()
    train_loss, train_correct = 0, 0
    
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        
        # 1. Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # 2. Backward pass (The math magic)
        optimizer.zero_grad() # Clear old gradients
        loss.backward()       # Calculate new gradients
        optimizer.step()      # Update weights
        
        train_loss += loss.item() * images.size(0)
        _, predicted = torch.max(outputs, 1)
        train_correct += (predicted == labels).sum().item()

    # --- VALIDATION PHASE ---
    model.eval()
    val_loss, val_correct = 0, 0
    
    with torch.no_grad(): # Don't calculate gradients here (saves memory)
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            val_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            val_correct += (predicted == labels).sum().item()

    # Calculate averages
    train_loss /= len(train_loader.dataset)
    train_acc = train_correct / len(train_loader.dataset)
    val_loss /= len(val_loader.dataset)
    val_acc = val_correct / len(val_loader.dataset)
    
    # Save to history
    history["train_loss"].append(train_loss)
    history["train_acc"].append(train_acc)
    history["val_loss"].append(val_loss)
    history["val_acc"].append(val_acc)

    print(f"Epoch [{epoch+1}/{epochs}] | Train Loss: {train_loss:.4f} | Val Acc: {val_acc:.4f}")
    

#final test
model.eval()
test_loss , test_correct = 0,0

with torch.no_grad(): # Don't calculate gradients here (saves memory)
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        test_loss += loss.item() * images.size(0)
        _, predicted = torch.max(outputs, 1)
        test_correct += (predicted == labels).sum().item()
# Calculate averages
test_loss /= len(test_loader.dataset)
test_acc = test_correct / len(test_loader.dataset)
# val_loss /= len(val_loader.dataset)
# val_acc = val_correct / len(val_loader.dataset)
print(f"final test =>  Model loss : {test_loss:.4f} | Test accuracy : {test_acc:.4f}")

#====================================testing===============================================

#load images from directory
tumorImg = Image.open("TumorTestImage.jpg").convert('RGB')
brainImg = Image.open("NormalTestImage.jpg").convert('RGB')
with torch.no_grad(): # Don't calculate gradients here cuz we dont need to train here
    model.eval()
    print(brain_dataset.class_to_idx) #getting class and label
    
    #unsqueeze add a dimension of size one ; allowing model that require
    #imageset to predict from only one image
    
    input_data = finalTestPreprocess(tumorImg).to(device)
    # print(input_data)
    # input_data = tumorImg.transform.toTensor().to(device)
    # transforms.ToTensor()
    y_preds = model(input_data.unsqueeze(0))
    predicted_class = torch.argmax(y_preds, dim=1).item()
    print(f"tumor prediction : class {predicted_class} ; {y_preds}")
    
    input_data = finalTestPreprocess(brainImg).to(device)
    y_preds = model(input_data.unsqueeze(0))
    predicted_class = torch.argmax(y_preds, dim=1).item()
    print(f"normal brain prediction : class {predicted_class} ; {y_preds}")
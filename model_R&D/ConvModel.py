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


batch_size = 16

image_height = 224
image_width = 224

#ImageFolder automatically one hot folder(no as 0,yes as 1) so we dont have to put label ourselves
brain_dataset =ImageFolder(root='brain_tumor_dataset', transform=None)

#get amount of output classes
classes_amount = len(brain_dataset.classes)
print(classes_amount)

image , label = next(iter(brain_dataset))
print(image,label)

#====================================model===============================================

class CNN_tumor(nn.Module):
    def __init__(self,in_channels,out_classes = 2):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels,out_channels = 32,kernel_size = 3)
        # self.reConv1 = nn.LazyConv2d(32,kernel_size = 3)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        # self.reConv2 = nn.LazyConv2d( 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        # self.reConv3 = nn.LazyConv2d(128, 3, padding=1)
        self.conv4 = nn.Conv2d(128, 256, 3, padding=1)
        # self.reConv4 = nn.LazyConv2d(256, 3, padding=1)
        # self.conv5 = nn.Conv2d(256, 512, 3, padding=1)
        # self.reConv5 = nn.Conv2d(512, 512, 3, padding=1)
        self.maxPool = nn.MaxPool2d(kernel_size=3)
        self.avgPool = nn.AdaptiveAvgPool2d((1,1))
        self.batchNorm1 = nn.BatchNorm2d(32)
        self.batchNorm2 = nn.BatchNorm2d(64)
        self.batchNorm3 = nn.BatchNorm2d(128)
        self.batchNorm4 = nn.BatchNorm2d(256)
        self.batchNorm5 = nn.BatchNorm2d(512)
        self.flatten = nn.Flatten()
        self.denseIn = nn.LazyLinear(256)
        self.dense = nn.Linear(256, 256)
        self.denseOut = nn.Linear(256, out_classes)
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()
        self.dropout = nn.Dropout(0.65)
        
    def forward(self,x):
        residual = x
        x = self.relu(self.batchNorm1(self.conv1(x)))
        x = self.maxPool(x)
        x = self.relu(self.batchNorm2(self.conv2(x)))
        x = self.maxPool(x)
        x = self.relu(self.batchNorm3(self.conv3(x)))
        x = self.maxPool(x)
        x = self.relu(self.batchNorm4(self.conv4(x)))
        x = self.maxPool(x)
        # x+= self.maxPool(self.maxPool(self.maxPool(self.maxPool(residual))))
        # x = self.relu(self.batchNorm5(self.conv5(x)))
        # x = self.maxPool(x)
        x = self.avgPool(x)
        x = self.flatten(x)
        x = self.relu(self.denseIn(x))
        x = self.dropout(x)
        x = self.relu(self.dense(x))
        x = self.dropout(x)
        return self.denseOut(x)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CNN_tumor(in_channels=3,out_classes=classes_amount).to(device)

# print(model)
# summary(model, input_size=(100,3,image_height,image_width))# (Batch Size, Channels, Height, Width)
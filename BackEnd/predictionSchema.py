from pydantic import BaseModel
from typing import List

class PredictionRequest(BaseModel):
    features: List[float]  # Input features

class PredictionResponse(BaseModel):
    prediction: int
    confidence: float
    probabilities: List[float]
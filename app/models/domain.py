from pydantic import BaseModel, Field
from typing import Optional, List

# Optimized based on RFE Analysis: Low importance fields are now Optional
class PCOSInput(BaseModel):
    # Numerical
    Age: int = Field(..., ge=10, le=100, description="Age in years (10-100)")
    Weight_kg: float = Field(..., gt=20, lt=200, description="Weight in kg")
    Height_cm: float = Field(..., gt=100, lt=250, description="Height in cm")
    Testosterone_ng_per_dL: float = Field(..., ge=0, description="Testosterone level")
    LH_FSH_Ratio: float = Field(..., ge=0, description="LH/FSH Ratio")
    Exercise_hrs_per_week: float = Field(..., ge=0, le=168, description="Hours of exercise per week")
    Sleep_hrs_per_night: float = Field(..., ge=0, le=24, description="Hours of sleep per night")
    Stress_score_0_10: int = Field(..., ge=0, le=10, description="Self-reported stress (0-10)")

    # Categorical / Binary (0 or 1)
    Hormonal_Imbalance: int = Field(..., ge=0, le=1)
    Hyperandrogenism: int = Field(..., ge=0, le=1)
    Hirsutism: int = Field(..., ge=0, le=1)
    Conception_Difficulty: int = Field(..., ge=0, le=1)
    Family_History_PCOS: int = Field(..., ge=0, le=1)
    Insulin_Resistance: int = Field(..., ge=0, le=1)
    Mental_Health: int = Field(..., ge=0, le=1)
    
    # Optional Fields (Low Importance per RFE)
    Diabetes: Optional[int] = Field(None, ge=0, le=1, description="Optional: History of Diabetes")
    Cardiovascular_Disease: Optional[int] = Field(None, ge=0, le=1, description="Optional: CVD History")
    Childhood_Trauma: Optional[int] = Field(None, ge=0, le=1, description="Optional")
    Family_History_Menstrual: Optional[int] = Field(None, ge=0, le=1, description="Optional")
    
    Smoking_Status: Optional[str] = Field(None, description="Never, Former, Current") 

    # Strings
    Menstrual_Cycle: str = Field(..., description="Regular, Irregular, Oligomenorrhea, Amenorrhea")
    
    # Optional Strings
    Diet_Type: Optional[str] = Field(None, description="Optional: Vegetarian, Non-vegetarian, Mixed, Vegan")
    Veg_or_NonVeg: Optional[str] = Field(None, description="Optional")

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    risk: str
    risk_class: str
    confidence_score: str
    uncertainty_metric: float
    recommendations: List[str]
    input_summary: dict

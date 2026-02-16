from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import PCOSInput, PredictionResponse
from app.services.prediction_service import prediction_service

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict(input_data: PCOSInput, db: Session = Depends(get_db)):
    """
    Predicts the likelihood of PCOS based on health and lifestyle factors.
    
    - **Step 1**: Validates input using Pydantic (strict type checking).
    - **Step 2**: Calls the AI Engine for a risk score (High/Moderate/Low).
    - **Step 3**: Saves the result to the Patient's History in PostgreSQL.
    - **Step 4**: Returns a detailed JSON report with recommendations.
    """
    try:
        return prediction_service.predict_risk(input_data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

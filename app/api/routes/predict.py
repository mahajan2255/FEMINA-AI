from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.domain import PCOSInput, PredictionResponse
from app.models.sql import User
from app.services.prediction_service import prediction_service
from app.api.auth_utils import get_current_user

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict(
    input_data: PCOSInput, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Predicts the likelihood of PCOS based on health and lifestyle factors.
    If authenticated, saves report to user history.
    """
    try:
        return prediction_service.predict_risk(input_data, db, user=current_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

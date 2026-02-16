from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.eli5_service import eli5_service

router = APIRouter()

@router.get("/reports/history/{patient_id}")
def get_history_comparison(patient_id: str, db: Session = Depends(get_db)):
    """
    Returns a temporal analysis (ELI5) of the patient's progress.
    Compares the most recent report with the one before it.
    """
    try:
        return eli5_service.compare_last_two_reports(patient_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

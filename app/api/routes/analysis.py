from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import PCOSInput
from app.services.protodash_service import protodash_service

router = APIRouter()

@router.post("/analysis/prototypes")
def analyze_prototypes(input_data: PCOSInput, db: Session = Depends(get_db)):
    """
    Identifies 'Prototypical' cases that match the current patient.
    Useful for 'Patients like you' analysis.
    """
    try:
        # We assume anonymous for now, or match based on input vector
        return protodash_service.get_prototypes("anonymous", input_data.dict(), db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

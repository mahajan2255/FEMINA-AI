from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.eli5_service import eli5_service
from app.models.sql import User
from app.api.auth_utils import get_current_user

router = APIRouter()

@router.get("/reports/history/me")
def get_my_history_comparison(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns a temporal analysis (ELI5) of the CURRENT USER'S progress.
    Compares the most recent report with the one before it.
    """
    try:
        return eli5_service.compare_last_two_reports(current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

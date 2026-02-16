from fastapi import APIRouter, HTTPException
from app.models.domain import PCOSInput
from app.services.explainability_service import explainability_service

router = APIRouter()

@router.post("/explain/local")
def explain_local(input_data: PCOSInput):
    """
    Generates a SHAP explanation for a specific patient.
    Returns the 'Why' behind the prediction.
    """
    try:
        return explainability_service.get_local_explanation(input_data.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

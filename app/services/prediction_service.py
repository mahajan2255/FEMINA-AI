from sqlalchemy.orm import Session
from app.ml.model_manager import model_manager
from app.models.domain import PCOSInput, PredictionResponse
from app.models.sql import PatientReport
import numpy as np

class PredictionService:
    
    @staticmethod
    def get_recommendations(data: dict):
        recs = []
        if data.get('Age', 0) > 35:
            recs.append("Since you are over 35, regular checkups specifically for metabolic health are recommended.")
        if data.get('Weight_kg', 0) > 80: 
            recs.append("Maintaining a healthy weight through diet and exercise can significantly improve PCOS symptoms.")
        if data.get('Insulin_Resistance', 0) == 1:
            recs.append("Monitor blood sugar levels and consider a low-glycemic index diet to manage insulin resistance.")
        if data.get('Stress_score_0_10', 0) > 7:
            recs.append("High stress can exacerbate PCOS symptoms. Consider stress management techniques like yoga or meditation.")
        if not recs:
            recs.append("Maintain a healthy lifestyle with balanced diet and regular exercise.")
        return recs

    @staticmethod
    def predict_risk(input_data: PCOSInput, db: Session):
        # Convert Pydantic model to dict
        data_dict = input_data.dict()
        
        # 1. Calls the Brain (Model Manager)
        prediction, prob, entropy = model_manager.predict(data_dict)
        
        # 2. Risk Logic
        if prob >= 0.75:
            risk = "High Risk"
            risk_class = "high"
        elif prob >= 0.35:
            risk = "Moderate Risk"
            risk_class = "moderate"
        else:
            risk = "Low Risk"
            risk_class = "low"
            
        # 3. Confidence Logic
        if entropy < 0.3:
            conf_status = "High Confidence"
        elif entropy < 0.5:
            conf_status = "Moderate Confidence"
        else:
            conf_status = "Uncertain/Ambiguous"
            
        # 4. Generate Recommendations
        recommendations = PredictionService.get_recommendations(data_dict)
        
        # 5. Save to Memory (Database)
        # Check if patient exists? For now, we just log every prediction as a report.
        # In a real app, we'd handle user authentication here.
        db_report = PatientReport(
            patient_id="anonymous", # Placeholder
            input_data=data_dict,
            prediction=int(prediction), # Explicit cast to native python int
            probability=float(prob),    # Explicit cast to native python float
            risk_level=risk,
            recommendations=recommendations
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        # 6. Return Response
        return PredictionResponse(
            prediction=prediction,
            probability=round(prob * 100, 2),
            risk=risk,
            risk_class=risk_class,
            confidence_score=conf_status,
            uncertainty_metric=round(entropy, 4),
            recommendations=recommendations,
            input_summary=data_dict
        )

prediction_service = PredictionService()

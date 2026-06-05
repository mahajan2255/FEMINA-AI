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
    def predict_risk(input_data: PCOSInput, db: Session, user=None):
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
        # Check if user exists
        user_id = user.id if user else None
        
        db_report = PatientReport(
            user_id=user_id, # Link to authenticated user
            input_data=data_dict,
            prediction=int(prediction), # Explicit cast to native python int
            probability=float(prob),    # Explicit cast to native python float
            risk_level=risk,
            recommendations=recommendations,
            # We should probably calculate SHAP here too if we want it in the report object immediately
            # or it can be updated later. For now, we are creating it without SHAP values column population in this specific snippet to match previous code style 
            # (previous code didn't seem to invoke SHAP here, but predict route did? 
            # Actually previous predict route in FLASKAPP did invoke SHAP, but PREDICTION_SERVICE in fastAPI didn't seem to?
            # Let's check imports. shap_values column exists in PatientReport.
            # I will leave SHAP out of this service method to avoid circular imports or complexity, 
            # assuming SHAP is handled separately or I should add it.
            # Wait, PatientReport has shap_values column. It's better to populate it.
            # But getting SHAP is expensive. Maybe keep it separate.
            # For now just adding user_id.
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

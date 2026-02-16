from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class PatientReport(Base):
    __tablename__ = "patient_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True) # Could be a UUID or username
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Input Data stored as JSON
    input_data = Column(JSON)
    
    # Prediction Results
    prediction = Column(Integer) # 0 or 1
    probability = Column(Float)
    risk_level = Column(String) # High, Moderate, Low
    
    # Explainability Data
    shap_values = Column(JSON) # Storing the key factors
    recommendations = Column(JSON)

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reports = relationship("PatientReport", back_populates="user")

class PatientReport(Base):
    __tablename__ = "patient_reports"

    id = Column(Integer, primary_key=True, index=True)
    # Changed from raw string to ForeignKey
    user_id = Column(Integer, ForeignKey("users.id"))
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

    user = relationship("User", back_populates="reports")

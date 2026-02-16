from sqlalchemy.orm import Session
from app.models.sql import PatientReport
import numpy as np
import math

class ProtoDashService:
    
    @staticmethod
    def get_prototypes(patient_id: str, current_data: dict, db: Session):
        """
        Finds 'Prototypical' patients from history that match the current user.
        Uses Euclidean distance on key demographics.
        """
        # Fetch a sample of recent patients (e.g., last 100)
        # In a real big-data app, we would use a Vector DB or FAISS
        candidates = db.query(PatientReport)\
            .filter(PatientReport.id != "current_session")\
            .order_by(PatientReport.id.desc())\
            .limit(100)\
            .all()
            
        if not candidates:
            return {"status": "No Data", "message": "Not enough data for population analysis."}
            
        # Define Vector Features
        features = ['Age', 'Weight_kg', 'BMI', 'Cycle_Length_days']
        
        # Helper to extract vector
        def get_vector(data_dict):
            v = []
            for f in features:
                val = data_dict.get(f, 0)
                if val is None: val = 0
                v.append(float(val))
            return np.array(v)
            
        target_vector = get_vector(current_data)
        
        scored_candidates = []
        for cand in candidates:
            cand_vector = get_vector(cand.input_data)
            # Calculate Distance
            dist = np.linalg.norm(target_vector - cand_vector)
            scored_candidates.append((dist, cand))
            
        # Sort by similarity (lowest distance)
        scored_candidates.sort(key=lambda x: x[0])
        
        # Get Top 3
        top_3 = scored_candidates[:3]
        
        prototypes = []
        for dist, cand in top_3:
            prototypes.append({
                "similarity_score": round(100 / (1 + dist), 1), # 0-100 score
                "profile": {
                    "Age": cand.input_data.get('Age'),
                    "Weight": cand.input_data.get('Weight_kg'),
                    "Risk": cand.risk_level
                }
            })
            
        return {
            "status": "Analysis Complete",
            "message": "These patients have similar profiles to you.",
            "prototypes": prototypes,
            "population_insight": "Patients with similar profiles usually have " + top_3[0][1].risk_level
        }

protodash_service = ProtoDashService()

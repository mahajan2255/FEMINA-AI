from sqlalchemy.orm import Session
from app.models.sql import PatientReport
from app.models.domain import PCOSInput

class ELI5Service:
    
    @staticmethod
    def compare_history(patient_id: str, current_data: dict, db: Session):
        """
        Compares the current patient state with their most recent previous record.
        Returns a 'Temporal Analysis' of what changed.
        """
        # Fetch the MOST RECENT previous report
        # We order by ID desc to get the latest one (assuming strictly sequential ID/time)
        previous_report = db.query(PatientReport)\
            .filter(PatientReport.patient_id == patient_id)\
            .order_by(PatientReport.id.desc())\
            .first()
            
        if not previous_report:
            return {
                "status": "No History",
                "message": "This is your first checkup. A baseline has been established."
            }
            
        prev_data = previous_report.input_data
        
        # Calculate Deltas
        changes = []
        
        # Key actionable features to track
        trackable_features = [
            'Weight_kg', 'BMI', 'Testosterone_ng_per_dL', 
            'Stress_score_0_10', 'Exercise_hrs_per_week', 'Sleep_hrs_per_night'
        ]
        
        for feature in trackable_features:
            curr_val = current_data.get(feature)
            prev_val = prev_data.get(feature)
            
            if curr_val is not None and prev_val is not None:
                delta = float(curr_val) - float(prev_val)
                if abs(delta) > 0.1: # Only report significant changes
                    valid_change = True
                    # Formatting logic
                    if feature == 'Weight_kg':
                        msg = f"Weight changed by {delta:+.1f}kg"
                    elif feature == 'Stress_score_0_10':
                        msg = f"Stress level {'increased' if delta > 0 else 'decreased'} by {abs(delta):.0f} points"
                    else:
                        msg = f"{feature} changed by {delta:+.2f}"
                        
                    changes.append({
                        "feature": feature,
                        "delta": delta,
                        "description": msg
                    })
        
        # Compare Probabilities
        risk_delta = 0.0
        if previous_report.probability is not None:
            # We assume we have the probability of the NEW prediction passed in somewhere, 
            # OR we just compare inputs. 
            # For this simplified service, we just return features. 
            pass

        return {
            "status": "Comparison Available",
            "previous_date": previous_report.timestamp,
            "changes": changes,
            "summary": f"Found {len(changes)} significant changes since your last visit."
        }
        
    @staticmethod
    def compare_last_two_reports(patient_id: str, db: Session):
        """
        Fetches the last two records from the DB and compares them.
        """
        history = db.query(PatientReport)\
            .filter(PatientReport.patient_id == patient_id)\
            .order_by(PatientReport.timestamp.desc())\
            .limit(2)\
            .all()
            
        if len(history) < 2:
            return {
                "status": "Insufficient History",
                "message": "Need at least 2 reports to generate a comparison."
            }
            
        latest = history[0]
        previous = history[1]
        
        # Reuse the logic
        return ELI5Service.compare_history(patient_id, latest.input_data, db)

eli5_service = ELI5Service()

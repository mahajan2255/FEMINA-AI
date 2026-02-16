from app.ml.shap_engine import shap_engine

class ExplainabilityService:
    
    @staticmethod
    def get_local_explanation(input_data: dict):
        """
        Returns the feature importance for a specific patient.
        """
        # Get raw SHAP values
        shap_map = shap_engine.explain_local(input_data)
        
        # Sort by absolute impact
        sorted_features = sorted(shap_map.items(), key=lambda item: abs(item[1]), reverse=True)
        
        # Format for API
        contributors = []
        for feature, impact in sorted_features:
            contributors.append({
                "feature": feature,
                "impact_score": impact,
                "direction": "RISK_INCREASING" if impact > 0 else "RISK_DECREASING"
            })
            
        return {
            "key_drivers": contributors[:5], # Top 5 drivers
            "all_features": contributors
        }

explainability_service = ExplainabilityService()

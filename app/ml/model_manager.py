import joblib
import pandas as pd
import numpy as np
import scipy.stats
import os

class ModelManager:
    _model = None
    MODEL_PATH = "pcos_nonlinear_stack_calibrated.joblib"
    
    # Define expected feature columns in exact order of training
    FEATURE_COLUMNS = [
        'Hormonal_Imbalance', 'Hyperandrogenism', 'Hirsutism', 'Testosterone_ng_per_dL',
        'Menstrual_Cycle', 'LH_FSH_Ratio', 'Conception_Difficulty', 'Family_History_PCOS',
        'Family_History_Menstrual', 'Insulin_Resistance', 'Diabetes', 'Cardiovascular_Disease',
        'Mental_Health', 'Childhood_Trauma', 'Age', 'Weight_kg', 'Height_cm',
        'Diet_Type', 'Veg_or_NonVeg', 'Exercise_hrs_per_week', 'Sleep_hrs_per_night',
        'Stress_score_0_10', 'Smoking_Status'
    ]

    @classmethod
    def load_model(cls):
        if cls._model is None:
            if os.path.exists(cls.MODEL_PATH):
                try:
                    cls._model = joblib.load(cls.MODEL_PATH)
                    print(f"Model loaded successfully from {cls.MODEL_PATH}")
                except Exception as e:
                    print(f"Error loading model: {e}")
                    raise e
            else:
                print(f"Model file not found at {cls.MODEL_PATH}")
                raise FileNotFoundError(f"Model file not found at {cls.MODEL_PATH}")
        return cls._model

    @classmethod
    def predict(cls, input_data: dict):
        model = cls.load_model()
        
        # Ensure column order matches training. Missing optional fields will be None/NaN
        ordered_data = {col: input_data.get(col) for col in cls.FEATURE_COLUMNS}
        input_df = pd.DataFrame([ordered_data])
        
        try:
            # Predict
            # Note: The model pipeline includes SimpleImputer which will handle None/NaN values
            print(f"DEBUG: Predicting with input shape: {input_df.shape}")
            probas = model.predict_proba(input_df)
            prob = probas[:, 1][0]
            prediction = int(prob >= 0.5)
            
            # Calculate Uncertainty
            entropy = cls.calculate_uncertainty(probas)
            
            return prediction, prob, entropy
        except Exception as e:
            import traceback
            print("CRITICAL ERROR IN MODEL PREDICTION:")
            print(traceback.format_exc())
            raise e

    @staticmethod
    def calculate_uncertainty(probabilities):
        """
        Calculate uncertainty using Entropy.
        Returns: entropy score (0 to ~0.69)
        """
        try:
            # Clip probabilities to avoid log(0)
            probs = np.clip(probabilities, 1e-10, 1 - 1e-10)
            entropy = scipy.stats.entropy(probs, axis=1)[0]
            return float(entropy)
        except Exception as e:
            print(f"Uncertainty calculation error: {e}")
            return 0.0

model_manager = ModelManager()

import joblib
import shap
import pandas as pd
import numpy as np
import os
import urllib.request
from app.ml.model_manager import model_manager
from app.core.config import settings

# Global wrapper for pickling
def global_predict_wrapper(x):
    # If x is a single row/array, convert to DataFrame
    if isinstance(x, np.ndarray):
        df = pd.DataFrame(x, columns=model_manager.FEATURE_COLUMNS)
    else:
        df = x
    return model_manager.load_model().predict_proba(df)[:, 1]

class SHAPEngine:
    _explainer = None
    EXPLAINER_PATH = settings.SHAP_EXPLAINER_PATH

    @classmethod
    def _ensure_explainer_file(cls):
        if os.path.exists(cls.EXPLAINER_PATH):
            return
        if settings.SHAP_EXPLAINER_URL:
            explainer_dir = os.path.dirname(cls.EXPLAINER_PATH)
            if explainer_dir:
                os.makedirs(explainer_dir, exist_ok=True)
            print(f"Downloading SHAP explainer from {settings.SHAP_EXPLAINER_URL}...")
            urllib.request.urlretrieve(settings.SHAP_EXPLAINER_URL, cls.EXPLAINER_PATH)
            return
        if os.getenv("VERCEL"):
            raise FileNotFoundError(
                "SHAP explainer not available. Set SHAP_EXPLAINER_URL for Vercel deployment."
            )

    @classmethod
    def get_explainer(cls):
        if cls._explainer is None:
            cls._ensure_explainer_file()
            if os.path.exists(cls.EXPLAINER_PATH):
                print(f"Loading SHAP explainer from {cls.EXPLAINER_PATH}...")
                cls._explainer = joblib.load(cls.EXPLAINER_PATH)
            else:
                print("SHAP explainer not found. Generating a new one (this may take time)...")
                cls._explainer = cls._create_explainer()
        return cls._explainer

    @classmethod
    def _create_explainer(cls):
        """
        Creates a KernelExplainer using synthetic background data.
        This matches the logic from the notebook/script provided.
        """
        # We don't need to load the model here for the wrapper, 
        # the wrapper loads it on demand or uses the singleton.
        
        # Generate synthetic background data (50 samples)
        n_background = 50
        background_data = {
            'Hormonal_Imbalance': np.random.choice([0, 1], n_background),
            'Hyperandrogenism': np.random.choice([0, 1], n_background),
            'Hirsutism': np.random.choice([0, 1], n_background),
            'Testosterone_ng_per_dL': np.random.uniform(10, 100, n_background),
            'Menstrual_Cycle': np.random.choice([0, 1], n_background), 
            'LH_FSH_Ratio': np.random.uniform(0.5, 3.0, n_background),
            'Conception_Difficulty': np.random.choice([0, 1], n_background),
            'Family_History_PCOS': np.random.choice([0, 1], n_background),
            'Family_History_Menstrual': np.random.choice([0, 1], n_background),
            'Insulin_Resistance': np.random.choice([0, 1], n_background),
            'Diabetes': np.random.choice([0, 1], n_background),
            'Cardiovascular_Disease': np.random.choice([0, 1], n_background),
            'Mental_Health': np.random.choice([0, 1], n_background),
            'Childhood_Trauma': np.random.choice([0, 1], n_background),
            'Age': np.random.randint(18, 45, n_background),
            'Weight_kg': np.random.uniform(50, 100, n_background),
            'Height_cm': np.random.uniform(150, 180, n_background),
            'Diet_Type': np.random.choice(['Veg', 'Non-Veg'], n_background),
            'Veg_or_NonVeg': np.random.choice([0, 1], n_background),
            'Exercise_hrs_per_week': np.random.uniform(0, 10, n_background),
            'Sleep_hrs_per_night': np.random.uniform(4, 9, n_background),
            'Stress_score_0_10': np.random.randint(0, 11, n_background),
            'Smoking_Status': np.random.choice([0, 1], n_background)
        }
        X_background = pd.DataFrame(background_data)
        
        # Use the global function
        explainer = shap.KernelExplainer(global_predict_wrapper, X_background)
        
        # Save for future use
        joblib.dump(explainer, cls.EXPLAINER_PATH)
        return explainer

    @classmethod
    def explain_local(cls, input_data: dict):
        """
        Generates SHAP values for a single prediction.
        """
        try:
            print("DEBUG: Getting SHAP Explainer...")
            explainer = cls.get_explainer()
            
            # Convert input dict to DataFrame with correct column order
            ordered_data = {col: input_data.get(col) for col in model_manager.FEATURE_COLUMNS}
            input_df = pd.DataFrame([ordered_data])
            print(f"DEBUG: Calculating SHAP values for shape {input_df.shape}...")
            
            # Calculate SHAP values
            # Passing numpy array to avoid column name conflicts/errors in simpler explainers
            shap_values = explainer.shap_values(input_df.values)
            print("DEBUG: SHAP values calculated.")
            
            # Handle different return types from shap_values (list vs array)
            if isinstance(shap_values, list):
                # For binary classification, index 1 usually corresponds to the positive class
                sv = shap_values[1][0]
            else:
                sv = shap_values[0]
                
            # Pair feature names with values
            explanation = {}
            for feat, val in zip(model_manager.FEATURE_COLUMNS, sv):
                explanation[feat] = float(val)
                
            return explanation
        except Exception as e:
            import traceback
            print("CRITICAL SHAP ERROR:")
            print(traceback.format_exc())
            raise e

shap_engine = SHAPEngine()

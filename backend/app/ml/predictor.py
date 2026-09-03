import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from app.ml.feature_engineering import case_dict_to_dataframe

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models_ml")

class MLPredictor:
    _models: Dict[str, Any] = {}

    @classmethod
    def is_trained(cls) -> bool:
        channels = ["email", "whatsapp", "voice"]
        for ch in channels:
            path = os.path.join(MODELS_DIR, f"{ch}_recovery_model.joblib")
            if not os.path.exists(path):
                return False
        return True

    @classmethod
    def load_models(cls):
        if not cls._models:
            if not cls.is_trained():
                raise FileNotFoundError("ML model artifacts missing in backend/models_ml/")
            channels = ["email", "whatsapp", "voice"]
            for ch in channels:
                path = os.path.join(MODELS_DIR, f"{ch}_recovery_model.joblib")
                cls._models[ch] = joblib.load(path)

    @classmethod
    def predict_channel_probabilities(cls, case_data: Dict[str, Any]) -> Dict[str, float]:
        cls.load_models()
        df = case_dict_to_dataframe(case_data)

        probabilities = {}
        for ch in ["email", "whatsapp", "voice"]:
            pipeline = cls._models[ch]
            prob_arr = pipeline.predict_proba(df)[:, 1]
            raw_p = float(prob_arr[0])
            clamped_p = round(max(0.01, min(0.99, raw_p)), 4)
            probabilities[ch] = clamped_p

        return probabilities

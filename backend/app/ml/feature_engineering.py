import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CATEGORICAL_FEATURES = [
    "payment_method",
    "bank",
    "failure_reason",
    "failure_category",
    "device_type",
    "risk_level"
]

NUMERIC_FEATURES = [
    "amount",
    "hour_of_day",
    "day_of_week",
    "previous_success_count",
    "previous_failure_count",
    "customer_success_rate",
    "attempt_number",
    "gateway_latency_ms"
]

def build_feature_preprocessor() -> ColumnTransformer:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES
            ),
            (
                "num",
                StandardScaler(),
                NUMERIC_FEATURES
            )
        ],
        remainder="drop"
    )
    return preprocessor

def prepare_features_df(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure all required columns exist with fallback defaults
    for col in CATEGORICAL_FEATURES:
        if col not in df.columns:
            df[col] = "unknown"
        else:
            df[col] = df[col].fillna("unknown").astype(str)

    for col in NUMERIC_FEATURES:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df[CATEGORICAL_FEATURES + NUMERIC_FEATURES]

def case_dict_to_dataframe(case_data: Dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame([case_data])
    return prepare_features_df(df)

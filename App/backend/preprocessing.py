import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "random_forest_credit_default.pkl")

_artifact = None

def get_model_artifact():
    global _artifact
    if _artifact is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        _artifact = joblib.load(MODEL_PATH)
    return _artifact

def preprocess_customer(row: dict) -> pd.DataFrame:
    artifact = get_model_artifact()
    features_order = artifact["features"]

    # Education mapping: 0 and 6 mapped to 5
    edu = 5 if row.get("EDUCATION") in (0, 6) else row.get("EDUCATION")

    # Sex mapping: 1 (Male) -> 0, 2 (Female) -> 1
    sex_mapped = 1 if row.get("SEX") == 2 else 0

    # Marriage: 1 -> Married, 2 -> Single, 3 -> Others (0 was baseline dropped)
    marriage = row.get("MARRIAGE")

    feat = {
        "LIMIT_BAL": row.get("LIMIT_BAL", 0),
        "SEX": sex_mapped,
        "AGE": row.get("AGE", 0),
        "PAY_1": row.get("PAY_0", 0),
        "PAY_2": row.get("PAY_2", 0),
        "PAY_3": row.get("PAY_3", 0),
        "PAY_4": row.get("PAY_4", 0),
        "PAY_5": row.get("PAY_5", 0),
        "PAY_6": row.get("PAY_6", 0),
        "BILL_AMT1": row.get("BILL_AMT1", 0),
        "BILL_AMT2": row.get("BILL_AMT2", 0),
        "BILL_AMT3": row.get("BILL_AMT3", 0),
        "BILL_AMT4": row.get("BILL_AMT4", 0),
        "BILL_AMT5": row.get("BILL_AMT5", 0),
        "BILL_AMT6": row.get("BILL_AMT6", 0),
        "PAY_AMT1": row.get("PAY_AMT1", 0),
        "PAY_AMT2": row.get("PAY_AMT2", 0),
        "PAY_AMT3": row.get("PAY_AMT3", 0),
        "PAY_AMT4": row.get("PAY_AMT4", 0),
        "PAY_AMT5": row.get("PAY_AMT5", 0),
        "PAY_AMT6": row.get("PAY_AMT6", 0),
        "EDUCATION_2": 1 if edu == 2 else 0,
        "EDUCATION_3": 1 if edu == 3 else 0,
        "EDUCATION_4": 1 if edu == 4 else 0,
        "EDUCATION_5": 1 if edu == 5 else 0,
        "MARRIAGE_1": 1 if marriage == 1 else 0,
        "MARRIAGE_2": 1 if marriage == 2 else 0,
        "MARRIAGE_3": 1 if marriage == 3 else 0,
    }

    df_sample = pd.DataFrame([feat])[features_order]
    return df_sample

def predict_risk(row: dict) -> dict:
    artifact = get_model_artifact()
    model = artifact["model"]
    threshold = float(artifact["threshold"])

    features_df = preprocess_customer(row)
    probability = float(model.predict_proba(features_df)[:, 1][0])
    prediction = int(probability >= threshold)

    if probability < 0.15:
        risk_level = "Low"
    elif probability < 0.35:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "prediction": prediction,
        "default": bool(prediction == 1),
        "probability": round(probability, 4),
        "risk_level": risk_level,
        "threshold": round(threshold, 4),
    }

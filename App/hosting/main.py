
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from preprocessing import preprocess

app = FastAPI(title="Credit Default Prediction API")

# Load the trained model artifact
artifact = joblib.load("random_forest_credit_default.pkl")

model = artifact["model"]
threshold = float(artifact["threshold"])
features = artifact["features"]



class CustomerFeatures(BaseModel):
    LIMIT_BAL: float = Field(description="Credit limit")
    SEX: int = Field(description="1 or 2")
    EDUCATION: int = Field(description="Education category")
    MARRIAGE: int = Field(description="Marriage category")
    AGE: int = Field(description="Customer age")

    PAY_0: int
    PAY_2: int
    PAY_3: int
    PAY_4: int
    PAY_5: int
    PAY_6: int

    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float

    PAY_AMT1: float
    PAY_AMT2: float
    PAY_AMT3: float
    PAY_AMT4: float
    PAY_AMT5: float
    PAY_AMT6: float


class PredictionRequest(BaseModel):
    features: CustomerFeatures



@app.get("/")
def home():
    return {
        "message": "Credit Default Prediction API is running"
    }


@app.post("/predict")
def predict(request: PredictionRequest):

    try:
        X = preprocess(request.features.model_dump(), features)

        probability = float(model.predict_proba(X)[0][1])

        prediction = int(probability >= threshold)

        return {
            "prediction": prediction,
            "probability": probability,
            "threshold": threshold,
            "result": "Default" if prediction == 1 else "No Default"
        }

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError
from database import add_customer, get_customers, add_prediction, get_predictions
from schemas import Customer
from preprocessing import predict_risk

app = FastAPI(title="CrediGuard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/customers")
def create_customer(customer_data: Customer):
    try:
        data = customer_data.model_dump()
        customer_id = add_customer(data)

        # Automatically generate and store risk assessment for this customer
        risk_result = predict_risk(data)
        prediction_record = {
            "customer_id": customer_id,
            "customer_summary": {
                "LIMIT_BAL": data["LIMIT_BAL"],
                "AGE": data["AGE"],
                "SEX": data["SEX"],
                "EDUCATION": data["EDUCATION"],
                "MARRIAGE": data["MARRIAGE"],
                "PAY_0": data["PAY_0"],
                "BILL_AMT1": data["BILL_AMT1"],
            },
            "prediction": risk_result["prediction"],
            "default": risk_result["default"],
            "default_probability": risk_result["probability"],
            "risk_level": risk_result["risk_level"],
            "threshold": risk_result["threshold"],
        }
        add_prediction(prediction_record)

        return {
            "success": True,
            "customer_id": customer_id,
            "message": "Customer added and risk evaluated successfully",
            "risk_assessment": risk_result
        }

    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="Unable to add customer."
        )


@app.get("/customers")
def list_customers():
    try:
        return {"customers": get_customers()}

    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch customers."
        )


@app.post("/predict")
def predict_customer_risk(customer_data: Customer):
    try:
        data = customer_data.model_dump()
        risk_result = predict_risk(data)

        prediction_record = {
            "customer_summary": {
                "LIMIT_BAL": data["LIMIT_BAL"],
                "AGE": data["AGE"],
                "SEX": data["SEX"],
                "EDUCATION": data["EDUCATION"],
                "MARRIAGE": data["MARRIAGE"],
                "PAY_0": data["PAY_0"],
                "BILL_AMT1": data["BILL_AMT1"],
            },
            "prediction": risk_result["prediction"],
            "default": risk_result["default"],
            "default_probability": risk_result["probability"],
            "risk_level": risk_result["risk_level"],
            "threshold": risk_result["threshold"],
        }
        prediction_id = add_prediction(prediction_record)

        return {
            "success": True,
            "prediction_id": prediction_id,
            "customer_summary": prediction_record["customer_summary"],
            **risk_result
        }

    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="Database error while saving prediction."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.get("/predictions")
def list_predictions():
    try:
        return {"predictions": get_predictions()}

    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch predictions."
        )

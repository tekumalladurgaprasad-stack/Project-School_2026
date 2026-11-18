from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError
from database import add_customer, get_customers
from schemas import Customer

app = FastAPI(title="CrediGuard")

# Lets the frontend (served from another port or opened as a file) call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/customers")
def create_customer(customer_data: Customer):
    try:
        customer_id = add_customer(
            customer_data.model_dump()
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "message": "Customer added successfully"
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

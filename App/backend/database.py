from pymongo import MongoClient

client = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=5000
)

client.admin.command("ping")

db = client["CrediGuard"]

customers = db["customers"]
predictions = db["predictions"]

def add_customer(customer_data):
    result = customers.insert_one(customer_data)
    return str(result.inserted_id)

def get_customers():
    return list(customers.find({}, {"_id": 0}))

def get_customer(customer_data):
    result = customers.find_one(customer_data, {"_id": 0})
    return result
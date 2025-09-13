import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, errors
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "assessment_db")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db["employees"]

try:
    collection.create_index([("employee_id", ASCENDING)], unique=True, background=True)
except errors.PyMongoError as e:
    print("Index creation error:", e)

employee_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["employee_id", "name", "department", "salary", "joining_date", "skills"],
        "properties": {
            "employee_id": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "department": {"bsonType": "string"},
            "salary": {"bsonType": ["int", "double"]},
            "joining_date": {"bsonType": "date"},
            "skills": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            }
        }
    }
}

try:
    if "employees" not in db.list_collection_names():
        db.create_collection("employees", validator=employee_validator, validationLevel="strict")
    else:
        db.command("collMod", "employees", validator=employee_validator, validationLevel="strict")
except errors.OperationFailure as e:
    print("Could not apply collection validator (collMod):", e)
except Exception as e:
    print("Validator creation error (ignored):", e)

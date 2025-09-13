from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime
from models.employee import Employee, UpdateEmployee
from db import collection
from utils import serialize_employee
from auth import verify_token
from pymongo.errors import DuplicateKeyError

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("/")
def create_employee(employee: Employee):
    """here we will create a new wmployee and this requires no jwt"""
    data = employee.dict()
    jd = data.get("joining_date")
    if not isinstance(jd, datetime):
        data["joining_date"] = datetime.combine(jd, datetime.min.time())

    try:
        collection.insert_one(data)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Employee created successfully"}



@router.get("/")
def list_employees(department: Optional[str] = Query(None)):
    """List employees (filtered by department, newest first)."""
    query = {}
    if department:
        query["department"] = department

    cursor = collection.find(query, {"_id": 0}).sort("joining_date", -1)
    employees = [serialize_employee(doc) for doc in cursor]

    return employees


@router.get("/avg-salary")
def avg_salary_by_department():
    pipeline = [
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
        {"$project": {"department": "$_id", "avg_salary": {"$round": ["$avg_salary", 2]}, "_id": 0}}
    ]
    return list(collection.aggregate(pipeline))


@router.get("/search")
def search_employees(skill: str):
    """we will Search the  employees by skill."""
    cursor = collection.find({"skills": {"$in": [skill]}}, {"_id": 0})
    return [serialize_employee(doc) for doc in cursor]

"authenticated routes"

@router.delete("/{employee_id}", dependencies=[Depends(verify_token)])
def delete_employee(employee_id: str):
    result = collection.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}

@router.put("/{employee_id}", dependencies=[Depends(verify_token)])
def update_employee(employee_id: str, updates: UpdateEmployee):
    update_data = {k: v for k, v in updates.dict().items() if v is not None}

    if "joining_date" in update_data:
        jd = update_data["joining_date"]
        if not isinstance(jd, datetime):
            update_data["joining_date"] = datetime.combine(jd, datetime.min.time())

    result = collection.update_one({"employee_id": employee_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"message": "Employee updated successfully"}



@router.get("/{employee_id}", dependencies=[Depends(verify_token)])
def get_employee(employee_id: str):
    
    employee = collection.find_one({"employee_id": employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return serialize_employee(employee)
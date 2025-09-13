from fastapi import APIRouter, HTTPException
from db import collection
from auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(employee_id: str):
    """
    Body: {"employee_id": "E123"}
    """
    user = collection.find_one({"employee_id": employee_id})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid employee_id")
    token = create_access_token({"employee_id": employee_id})
    return {"access_token": token, "token_type": "bearer"}

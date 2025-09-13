from fastapi import FastAPI
from routes import employees, auth as auth_router

app = FastAPI(title="Employee Management API (Assessment)")

app.include_router(auth_router.router)
app.include_router(employees.router)

@app.get("/")
def root():
    return {"message": "Employee Management API. See /docs for interactive API docs."}

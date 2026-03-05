from fastapi import FastAPI
from app.routers import department, employee

app = FastAPI(title="Company Org API")

app.include_router(department.router)
app.include_router(employee.router)
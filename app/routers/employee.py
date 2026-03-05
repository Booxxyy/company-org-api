from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_session
from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.repositories.employee import create_employee

router = APIRouter(prefix="/employee", tags=["Employees"])

@router.post("/", response_model=EmployeeRead,status_code=201)
def create(data: EmployeeCreate,
    session: Session = Depends(get_session),):
    return create_employee(session, data)
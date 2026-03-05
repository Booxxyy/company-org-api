from app.models.department import Department
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate
from sqlalchemy.orm import Session
from fastapi import HTTPException

def create_employee(
        session: Session,
        department_id: int,
        data: EmployeeCreate,
) -> Employee:
    dept = session.get(Department, department_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")

    employee = Employee(
        department_id = department_id,
        full_name = data.full_name,
        position = data.position,
        hired_at = data.hired_at,
    )
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee
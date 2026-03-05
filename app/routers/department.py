from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_session
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentTree, DepartmentRead
from app.repositories.department import (
    create_department,
    get_department_tree,
    update_department,
    delete_department_cascade,
    delete_department_reassign,
)

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=DepartmentRead, status_code=201)
def create(data: DepartmentCreate, session: Session = Depends(get_session)):
    return create_department(session, data)

@router.get("/{department_id}/tree", response_model=DepartmentTree)
def get_tree(
        department_id: int,
        depth: int = Query(default=1, ge=1, le=5),
        include_employees: bool = Query(default=True),
        session: Session = Depends(get_session),
):
    return get_department_tree(session, department_id, depth, include_employees)

@router.patch("/{department_id}", response_model=DepartmentRead)
def update(
        department_id: int,
        data: DepartmentUpdate,
        session: Session = Depends(get_session),
):
    return update_department(session, department_id, data)

@router.delete("/{department_id}/cascade", status_code=204)
def delete_cascade(department_id: int, session: Session = Depends(get_session)):
    delete_department_cascade(session, department_id)

@router.delete("/{department_id}/reassign", status_code=204)
def delete_reassign(
        department_id: int,
        reassign_to_id: int = Query(...),
        session: Session = Depends(get_session),
):
    delete_department_reassign(session, department_id, reassign_to_id)
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.schemas.employee import EmployeeRead



class DepartmentCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Поле name не может быть пустым")
        if len(v) > 200:
            raise ValueError("Поле name не может быть длиннее 200 символов")
        return v

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Поле name не может быть пустым")
        if len(v) > 200:
            raise ValueError("Поле name не может быть длиннее 200 символов")
        return v

class DepartmentRead(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}

class DepartmentTree(BaseModel):
    department: DepartmentRead
    employees: list[EmployeeRead] = []
    children: list["DepartmentTree"] = []

    model_config = {"from_attributes": True}
from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class EmployeeCreate(BaseModel):
    full_name: str
    position: str
    hired_at: Optional[date] = None

    @field_validator("full_name", "position")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Поле не может быть пустым")
        if len(v) > 200:
            raise ValueError("Поле не может быть длиннее 200 символов")
        return v

class EmployeeRead(BaseModel):
    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: Optional[date] = None
    created_at: datetime

    model_config = {"from_attributes": True}
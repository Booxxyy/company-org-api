from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    department_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete = "CASCADE"),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(200), nullable = False)
    position: Mapped[str] = mapped_column(String(200), nullable = False)
    hired_at: Mapped[Optional[date]] = mapped_column(Date, nullable = True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="employees",
    )
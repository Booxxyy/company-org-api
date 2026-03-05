from datetime import datetime, timezone

from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("parent_id", "name", name="uq_dept_parent_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    parent: Mapped["Department | None"] = relationship(
        "Department",
        back_populates="children",
        remote_side="Department.id",
    )
    children: Mapped[list["Department"]] = relationship(
        "Department",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete-orphan",
    )
from __future__ import annotations
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, ForeignKey
from app.infra.db import db

if TYPE_CHECKING:
    from app.infra.entities.task_db import TaskDB

    
class TaskStatusDB(db.Model):
    __tablename__ = "task_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    tasks: Mapped[List[TaskDB]] = relationship(back_populates="status")

    def __repr__(self):
        return f"<TaskStatusDB {self.name}>"

from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from app.infra.db import db

if TYPE_CHECKING:
    from app.infra.entities.task_status_db import TaskStatusDB
    from app.infra.entities.project_db import ProjectDB

    
class TaskDB(db.Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    identificator: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("task_status.id"), nullable=False)

    project: Mapped[ProjectDB] = relationship(back_populates="tasks")
    status: Mapped[TaskStatusDB] = relationship(back_populates="tasks")



    def __repr__(self):
        return f"<TaskDB {self.title}>"

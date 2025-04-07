from __future__ import annotations
from typing import TYPE_CHECKING, List

import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, ForeignKey
from app.infra.db import db

if TYPE_CHECKING:
    from app.infra.entities.user_db import UserDB
    from app.infra.entities.task_db import TaskDB
    from app.infra.entities.focus_session_db import FocusSessionDB


class ProjectDB(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    identificator: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped[UserDB] = relationship(back_populates="projects")
    tasks: Mapped[List[TaskDB]] = relationship(back_populates="project", cascade="all, delete-orphan")
    focus_sessions: Mapped[List[FocusSessionDB]] = relationship(back_populates="project", cascade="all, delete-orphan")



    def __repr__(self):
        return f"<ProjectDB {self.title}>"

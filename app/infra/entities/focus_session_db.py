from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, DateTime
from app.infra.db import db

if TYPE_CHECKING:
    from app.infra.entities.project_db import ProjectDB


class FocusSessionDB(db.Model):
    __tablename__ = "focus_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped[ProjectDB] = relationship(back_populates="focus_sessions")

    def __repr__(self):
        return f"<FocusSessionDB {self.start_time} - {self.duration_seconds}s>"

from __future__ import annotations
from typing import TYPE_CHECKING, List

import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer
from app.infra.db import db

if TYPE_CHECKING:
    from app.infra.entities.project_db import ProjectDB


class UserDB(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    identificator: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    projects: Mapped[List[ProjectDB]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserDB {self.username}>"

from typing import Optional, TYPE_CHECKING

# Assume que TaskStatusValidationError será definido em app/models/exceptions.py
from app.models.exceptions import TaskStatusValidationError
from app.infra.entities.task_status_db import TaskStatusDB



class TaskStatus:
    # NAME_MAX_LEN = 255

    def __init__(self, name: str):
        self._id: Optional[int] = None  
        self.name = name

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def name(self) -> str:
        return self._name
    
    @classmethod
    def from_orm(cls, status_db: 'TaskStatusDB') -> Optional['TaskStatus']:
        if not status_db:
            return None
        instance = cls(name=status_db.name)
        instance._id = status_db.id
        return instance

    # @name.setter
    # def name(self, value: str):
    #     if not value or not isinstance(value, str):
    #         raise TaskStatusValidationError(field="name", message="O nome do status é obrigatório.")
    #     if len(value) > self.NAME_MAX_LEN:
    #         raise TaskStatusValidationError(field="name", message=f"O nome do status não pode exceder {self.NAME_MAX_LEN} caracteres.")
    #     self._name = value

    # --- Métodos de Mapeamento ORM ---

  

    # def to_orm(self) -> 'TaskStatusDB':
    #     status_db = TaskStatusDB(
    #         name=self.name
    #     )
    #     if self.id is not None:
    #         status_db.id = self.id

    #     return status_db

    # --- Métodos Utilitários ---

    def __repr__(self) -> str:
        return f"<TaskStatus(id={self.id}, name='{self.name}')>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskStatus):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


# /home/gccintra/projects/focus_time_v2/app/models/focus_session.py

from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING


from app.models.exceptions import FocusSessionValidationError
from app.infra.entities.focus_session_db import FocusSessionDB

if TYPE_CHECKING:
    from app.models.project import Project


class FocusSession:
    def __init__(
        self,
        project: 'Project',
        started_at: datetime,
        duration_seconds: int,
    ):
        self._id: Optional[int] = None 


        self.project = project
        self.started_at = started_at
        self.duration_seconds = duration_seconds

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def project(self) -> 'Project':
        return self._project

    @project.setter
    def project(self, value: 'Project'):
        from app.models.project import Project
        if value is None:
            raise FocusSessionValidationError(field="project", message="O projeto é obrigatório.")
        if not isinstance(value, Project):
            raise FocusSessionValidationError(field="project", message="Objeto Project inválido fornecido.")
        self._project = value

    @property
    def started_at(self) -> datetime:
        return self._started_at

    @started_at.setter
    def started_at(self, value: datetime):
        if value is None or not isinstance(value, datetime):
            raise FocusSessionValidationError(field="started_at", message="O tempo de início (started_at) é obrigatório e deve ser um datetime.")
        self._started_at = value

    @property
    def duration_seconds(self) -> int:
        return self._duration_seconds

    @duration_seconds.setter
    def duration_seconds(self, value: int):
        if value is None or not isinstance(value, int):
            raise FocusSessionValidationError(field="duration_seconds", message="A duração em segundos é obrigatória e deve ser um inteiro.")
        if value < 0:
            raise FocusSessionValidationError(field="duration_seconds", message="A duração em segundos não pode ser negativa.")
        self._duration_seconds = value

    @property
    def end_time(self) -> datetime:
        return self.started_at + timedelta(seconds=self.duration_seconds)

    # --- Métodos de Mapeamento ORM ---

    @classmethod
    def from_orm(cls, session_db: 'FocusSessionDB') -> Optional['FocusSession']:
        if not session_db:
            return None

        from app.models.project import Project

        if not session_db.project:
            raise ValueError(f"Relação Project não carregada para FocusSessionDB id {session_db.id}")
        project_domain = Project.from_orm(session_db.project)
        if not project_domain:
             raise ValueError(f"Não foi possível criar o objeto de domínio Project a partir do projeto de FocusSessionDB id {session_db.id}")

        instance = cls(
            project=project_domain,
            started_at=session_db.started_at,
            duration_seconds=session_db.duration_seconds
        )
        instance._id = session_db.id
        return instance

    def to_orm(self) -> 'FocusSessionDB':

        session_db = FocusSessionDB(
            started_at=self.started_at,
            duration_seconds=self.duration_seconds
        )

        if self.id is not None:
            session_db.id = self.id

        return session_db

    # --- Métodos Utilitários ---

    def __repr__(self) -> str:
        project_title = getattr(self.project, 'title', 'N/A')
        start_str = self.started_at.strftime('%Y-%m-%d %H:%M:%S')
        return f"<FocusSession(id={self.id}, project='{project_title}', started='{start_str}', duration={self.duration_seconds}s)>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FocusSession):
            return NotImplemented
        if self.id is not None and other.id is not None:
            return self.id == other.id
        return (self.project == other.project and
                self.started_at == other.started_at and
                self.duration_seconds == other.duration_seconds)

    def __hash__(self) -> int:
        if self.id is not None:
            return hash(self.id)

        return hash((self.project, self.started_at, self.duration_seconds))


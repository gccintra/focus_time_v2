import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from app.models.exceptions import TaskValidationError
from app.infra.entities.task_db import TaskDB

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task_status import TaskStatus
    # from app.infra.entities.project_db import ProjectDB
    # from app.infra.entities.task_status_db import TaskStatusDB


class Task:
    """Representa uma Tarefa no domínio da aplicação."""
    TITLE_MAX_LEN = 255
    DESC_MAX_LEN = 255

    def __init__(
        self,
        title: str,
        project: 'Project',
        status: 'TaskStatus', 
        created_at: Optional[datetime] = None,
        identificator: Optional[str] = None,
        description: Optional[str] = None,
        completed_at: Optional[datetime] = None
    ):
        self._identificator = identificator if identificator is not None else str(uuid.uuid4())

        self.title = title
        self.description = description 
        self.project = project
        self.status = status 

        created_at_value_to_set = created_at if created_at is not None else datetime.now()
        self.created_at = created_at_value_to_set

        self.completed_at = completed_at


    @property
    def identificator(self) -> str:
        return self._identificator

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not value or not isinstance(value, str):
            raise TaskValidationError(field="title", message="O título é obrigatório e deve ser uma string.")
        if len(value) > self.TITLE_MAX_LEN:
             raise TaskValidationError(field="title", message=f"O título não pode exceder {self.TITLE_MAX_LEN} caracteres.")
        self._title = value

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: Optional[str]):
        if value is not None:
            if not isinstance(value, str):
                 raise TaskValidationError(field="description", message="A descrição deve ser uma string ou None.")
            if len(value) > self.DESC_MAX_LEN:
                 raise TaskValidationError(field="description", message=f"A descrição não pode exceder {self.DESC_MAX_LEN} caracteres.")
        self._description = value 

    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @created_at.setter
    def created_at(self, value: Optional[datetime]):
        if value is None:
            raise TaskValidationError(field="created_at", message="created_at não pode ser definido como None após a inicialização.")
        if not isinstance(value, datetime):
            raise TaskValidationError(field="created_at", message="created_at deve ser um objeto datetime.")
        self._created_at = value
   
    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at
    
    @completed_at.setter
    def completed_at(self, value: Optional[datetime]):
        if value is not None and not isinstance(value, datetime):
            raise TaskValidationError(field="completed_at", message="completed_at deve ser um objeto datetime ou None.")
        self._completed_at = value

    @property
    def project(self) -> 'Project':
        return self._project

    @project.setter
    def project(self, value: 'Project'):
        from app.models.project import Project
        if value is None:
            raise TaskValidationError(field="project", message="O projeto é obrigatório.")
        if not isinstance(value, Project):
            raise TaskValidationError(field="project", message="Objeto Project inválido fornecido.")
        self._project = value

    @property
    def status(self) -> 'TaskStatus':
        return self._status

    @status.setter
    def status(self, value: 'TaskStatus'):
        from app.models.task_status import TaskStatus
        if value is None:
             raise TaskValidationError(field="status", message="O status é obrigatório.")
        if not isinstance(value, TaskStatus):
             raise TaskValidationError(field="status", message="Objeto TaskStatus inválido fornecido.")
        self._status = value

    

    # --- Métodos de mudança de estado ---

    def complete(self, status_completed: 'TaskStatus'):
        from app.models.task_status import TaskStatus
        if not isinstance(status_completed, TaskStatus):
            raise TaskValidationError(field="status_completed", message="Objeto TaskStatus inválido fornecido para conclusão.")

        if self._completed_at is None:
            self._completed_at = datetime.now()
        self.status = status_completed 

    def reopen(self, status_reopened: 'TaskStatus'):
        from app.models.task_status import TaskStatus
        if not isinstance(status_reopened, TaskStatus):
            raise TaskValidationError(field="status_reopened", message="Objeto TaskStatus inválido fornecido para reabertura.")

        self._completed_at = None
        self.status = status_reopened 

    # --- Métodos de Mapeamento ORM ---

    @classmethod
    def from_orm(cls, task_db: 'TaskDB') -> Optional['Task']:
        if not task_db:
            return None

        from app.models.project import Project
        from app.models.task_status import TaskStatus

        if not task_db.project:
            raise ValueError(f"Relação Project não carregada para TaskDB id {task_db.id}")
        project_domain = Project.from_orm(task_db.project)
        if not project_domain:
            raise ValueError(f"Não foi possível criar o objeto de domínio Project a partir do projeto de TaskDB id {task_db.id}")

        if not task_db.status:
            raise ValueError(f"Relação Status não carregada para TaskDB id {task_db.id}")
        status_domain = TaskStatus.from_orm(task_db.status) 
        if not status_domain:
            raise ValueError(f"Não foi possível criar o objeto de domínio TaskStatus a partir do status de TaskDB id {task_db.id}")

      #try
        return cls(
            identificator=task_db.identificator,
            title=task_db.title,
            description=task_db.description,
            created_at=task_db.created_at,
            completed_at=task_db.completed_at,
            project=project_domain, 
            status=status_domain    
        )

    def to_orm(self) -> 'TaskDB':
        """
        Cria um objeto TaskDB (entidade do banco de dados) a partir do objeto de domínio Task.
        Nota: Chaves estrangeiras (project_id, status_id) e relações (project, status)
        NÃO são definidas aqui. O repositório/serviço é responsável por associar
        esta instância TaskDB com as instâncias ProjectDB e TaskStatusDB corretas.
        """
       
        return TaskDB(
            identificator=self.identificator,
            title=self.title,
            description=self.description,
            created_at=self.created_at,
            completed_at=self.completed_at
            # project_id, status_id, project, status são omitidos intencionalmente
        )

    # --- Métodos Utilitários ---

    def __repr__(self) -> str:
       
        status_name = getattr(self.status, 'name', 'N/A')
        project_title = getattr(self.project, 'title', 'N/A')
        return (f"<Task(identificator='{self.identificator}', title='{self.title}', "
                f"project='{project_title}', status='{status_name}')>")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        # A igualdade de negócio é definida pelo identificador único
        return self.identificator == other.identificator

    def __hash__(self) -> int:
        return hash(self.identificator)


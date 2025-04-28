import uuid
from app.utils.logger import logger
from app.models.exceptions import ProjectValidationError # Assuming you create this in exceptions.py
from app.infra.entities.project_db import ProjectDB
  

class Project():
    TITLE_MAX_LEN = 255 
    COLOR_MAX_LEN = 255 

    def __init__(self,
                user_identificator: str, 
                title: str,
                color: str,
                identificator = None,
                active: bool = True): 

        self._identificator = identificator if identificator is not None else str(uuid.uuid4())
        self.user_identificator = user_identificator 
        self.title = title 
        self.color = color 
        self.active = active 


    @property
    def identificator(self) -> str:
        return self._identificator

    @property
    def user_identificator(self) -> str:
        return self._user_identificator

    @user_identificator.setter
    def user_identificator(self, value: str):
        if not value:
            raise ProjectValidationError(field="user_identificator", message="User identificator cannot be empty.")
        try:
            uuid.UUID(value, version=4)
        except ValueError:
            raise ProjectValidationError(field="user_identificator", message="Invalid User UUID format.")
        self._user_identificator = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not value:
            raise ProjectValidationError(field="title", message="Project title cannot be empty.")
        if len(value) > self.TITLE_MAX_LEN:
            raise ProjectValidationError(field="title", message=f"Project title must be at most {self.TITLE_MAX_LEN} characters.")
        self._title = value

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        if not value:
            raise ProjectValidationError(field="color", message="Project color cannot be empty.")
        if len(value) > self.COLOR_MAX_LEN:
             raise ProjectValidationError(field="color", message=f"Project color must be at most {self.COLOR_MAX_LEN} characters.")
        self._color = value

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        if not isinstance(value, bool):
            raise ProjectValidationError(field="active", message="'active' must be a boolean value.")
        self._active = value

   
    # --- ORM Mapping Methods ---

    @classmethod
    def from_orm(cls, project_db: 'ProjectDB') -> 'Project':
        if not project_db:
            return None

        if not project_db.user or not project_db.user.identificator:
            logger.warning(f"Warning: User or User identificator missing for ProjectDB id {project_db.id}. Cannot fully map to Project domain model.")
            raise ValueError(f"User relationship not loaded or user identificator missing for ProjectDB id {project_db.id}")


        return cls(
            identificator=project_db.identificator,
            user_identificator=project_db.user.identificator, 
            title=project_db.title,
            color=project_db.color,
            active=project_db.active
        )

    def to_orm(self) -> 'ProjectDB':

        return ProjectDB(
            identificator=self.identificator,
            title=self.title,
            color=self.color,
            active=self.active
            # user_id is intentionally omitted here. 
        )


    def __repr__(self) -> str:
        return f"<Project(identificator='{self.identificator}', title='{self.title}', user='{self.user_identificator}')>"


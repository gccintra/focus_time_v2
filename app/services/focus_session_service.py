from app.infra.entities.project_db import ProjectDB
from app.infra.repository.project_repository import ProjectRepository
from app.models.project import Project
from ..models.focus_session import FocusSession
from ..infra.repository.focus_session_repository import FocusSessionRepository
from app.models.exceptions import FocusSessionValidationError

from typing import List, Dict, Any, Optional 
from datetime import date, timedelta, datetime
from ..models.exceptions import ProjectNotFoundError, ProjectValidationError, DatabaseError, AuthorizationError, UserNotFoundError
from ..utils.logger import logger


class FocusSessionService:
    def __init__(self):
        from app.services.project_service import ProjectService
        self.project_service = ProjectService()
        self.project_repo = ProjectRepository()
        self.repo = FocusSessionRepository()
       

    def _find_project_db_by_id_only(self, project_id: str) -> Optional['ProjectDB']:
        """Helper para buscar ProjectDB apenas por ID usando o repo injetado."""
        logger.debug(f"Service: Finding project DB by id '{project_id}' (no user filter)")
        try:
            project_db = self.project_repo.find_by_id_with_user(project_identificator=project_id) 
            return project_db
        except DatabaseError as e:
            logger.error(f"Service: Error finding project DB by id '{project_id}': {e}", exc_info=True)
            raise #

    def save_focus_session(self, user_id: str, project_id: str, started_at: datetime, duration_seconds: int) -> FocusSession:
        logger.info(f"Service: Attempting to save focus session for project '{project_id}' by user '{user_id}'")

        try:
            if duration_seconds <= 0:
                raise FocusSessionValidationError(field="duration_seconds", message="duration of focus session cannot be under or equal 0 seconds.")

            project_db_check = self._find_project_db_by_id_only(project_id)

            if project_db_check is None:
                logger.warning(f"Service: Project '{project_id}' not found.")
                raise ProjectNotFoundError(project_id=project_id)

            if project_db_check.user is None or project_db_check.user.identificator != user_id:
                owner_id = project_db_check.user.identificator if project_db_check.user else "unknown"
                logger.error(f"Service: Authorization failed. User '{user_id}' attempted action on project '{project_id}' owned by '{owner_id}'.")
                raise AuthorizationError(user_id=user_id, resource_id=project_id, message="User does not own this project.")
   
    
            try:
                project_domain = Project.from_orm(project_db_check)
                if not project_domain: 
                    raise ValueError("Failed to convert found ProjectDB to domain object.")
            except ValueError as e:
                logger.error(f"Service: Error converting ProjectDB to Project domain object for id '{project_id}': {e}", exc_info=True)
                raise DatabaseError(f"Error processing project data for project '{project_id}'.")

            new_focus_session = FocusSession(
                project=project_domain, 
                started_at=datetime.fromisoformat(started_at),
                duration_seconds=duration_seconds
            )

            self.repo.add(new_focus_session)
            self.repo._session.commit() 

            logger.info(f"Focus session (Domain ID: {new_focus_session.id}) saved successfully for project '{project_id}' by user '{user_id}'")
            return new_focus_session

        except (ProjectNotFoundError, AuthorizationError, FocusSessionValidationError, ProjectValidationError) as e: 
            self.repo._session.rollback()
            log_level = logger.error if isinstance(e, AuthorizationError) else logger.warning
            log_level(f"Service: Failed to save focus session for user '{user_id}', project '{project_id}'. Reason: {type(e).__name__}: {e}")
            raise #

        except DatabaseError as e: 
            self.repo._session.rollback()
            logger.error(f"Service: Database error saving focus session for project '{project_id}' by user '{user_id}': {e}", exc_info=True)
            raise #

        except Exception as e:
            self.repo._session.rollback()
            logger.error(f"Service: Unexpected error saving focus session for project '{project_id}' by user '{user_id}': {e}", exc_info=True)
            raise DatabaseError("An unexpected error occurred while saving the focus session.")

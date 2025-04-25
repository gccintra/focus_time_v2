# /home/gccintra/projects/focus_time_v2/app/infra/repository/focus_session_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, MultipleResultsFound
from sqlalchemy import select
from typing import Optional

from app.infra.db import db
from app.infra.entities.focus_session_db import FocusSessionDB
from app.infra.entities.project_db import ProjectDB
from app.models.focus_session import FocusSession
from app.models.project import Project # Import Project domain model for type hinting if needed
from app.models.exceptions import DatabaseError, ProjectNotFoundError, FocusSessionValidationError
from app.utils.logger import logger

class FocusSessionRepository:
    def __init__(self, session: Session = db.session):
        self._session = session

    def _find_project_db_by_identificator(self, project_identificator: str) -> Optional[ProjectDB]:
        logger.debug(f"Repository: Finding project DB by identificator '{project_identificator}'")
        try:
            stmt = select(ProjectDB).where(ProjectDB.identificator == project_identificator)
            project_db = self._session.execute(stmt).scalar_one_or_none()
            if project_db:
                logger.debug(f"Repository: Project DB found for identificator '{project_identificator}' (ID: {project_db.id})")
            else:
                logger.debug(f"Repository: Project DB not found for identificator '{project_identificator}'")
            return project_db
        except MultipleResultsFound:
            logger.error(f"Database integrity error: Multiple projects found with identificator {project_identificator}")
            raise DatabaseError(f"Data integrity issue: multiple projects found for identificator {project_identificator}.")
        except SQLAlchemyError as e:
            logger.error(f"Database error finding project by identificator {project_identificator}: {e}", exc_info=True)
            raise DatabaseError(f"Error accessing project data for identificator {project_identificator}.")


    def add(self, focus_session: FocusSession) -> None:
        logger.debug(f"Repository: Attempting to add focus session for project '{focus_session.project.identificator}' starting at '{focus_session.started_at}'")
        try:
            if focus_session.duration_seconds <= 0:
                raise FocusSessionValidationError(field="duration_seconds", message="duration of focus session cannot be under or equal 0 seconds.")

            project_db = self._find_project_db_by_identificator(focus_session.project.identificator)
            if not project_db:
                logger.error(f"Repository: Project with identificator {focus_session.project.identificator} not found. Cannot add focus session.")
                raise ProjectNotFoundError(project_id=focus_session.project.identificator)

            focus_session_db = focus_session.to_orm()

            focus_session_db.project_id = project_db.id
            # Alternatively, if relationships are set up correctly, you might assign the object:
            # focus_session_db.project = project_db

            self._session.add(focus_session_db)

            self._session.flush()

            if focus_session_db.id is not None and focus_session.id is None:
                focus_session._id = focus_session_db.id # Access private attribute carefully or add a setter

            logger.info(f"Repository: Focus session (DB ID: {focus_session_db.id}) added and flushed to session for project ID {project_db.id}.")
        except FocusSessionValidationError as e:
            logger.warning(f"Repository: Failed to add focus session because durantion seconds are not valid (minor or equal to 0).")
            raise
        except ProjectNotFoundError:
            logger.warning(f"Repository: Failed to add focus session because project '{focus_session.project.identificator}' was not found.")
            raise
        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Repository: Database error adding/flushing focus session for project '{focus_session.project.identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to add focus session for project '{focus_session.project.title}' to the database session.")
        except Exception as e:
             logger.error(f"Repository: Unexpected error adding focus session for project '{focus_session.project.identificator}': {e}", exc_info=True)
             raise DatabaseError(f"An unexpected error occurred while adding the focus session.")

    # --- Outros métodos (get_by_id, get_by_project, update, delete, etc.) serão adicionados aqui futuramente ---


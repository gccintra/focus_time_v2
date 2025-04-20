from sqlalchemy.orm import joinedload, Session
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound, IntegrityError
from sqlalchemy import select
from typing import List, Optional

from app.infra.db import db
from app.infra.entities.project_db import ProjectDB
from app.infra.entities.task_db import TaskDB
from app.infra.entities.user_db import UserDB
from app.models.project import Project
from app.models.task import Task
from app.models.focus_session import FocusSession
from app.models.dtos.project_dto import ProjectDetailsDTO
from app.models.exceptions import ProjectNotFoundError, DatabaseError, UserNotFoundError 
from app.utils.logger import logger

class ProjectRepository:
    def __init__(self, session: Session = db.session):
        self._session = session

    def _find_user_db_by_identificator(self, user_identificator: str) -> Optional[UserDB]:
        logger.debug(f"Repository: Finding user DB by identificator '{user_identificator}'")
        try:
            stmt = select(UserDB).where(UserDB.identificator == user_identificator)
            user_db = self._session.execute(stmt).scalar_one_or_none()
            if user_db:
                logger.debug(f"Repository: User DB found for identificator '{user_identificator}'")
            else:
                 logger.debug(f"Repository: User DB not found for identificator '{user_identificator}'")
            return user_db
        except MultipleResultsFound:
            logger.error(f"Database integrity error: Multiple users found with identificator {user_identificator}")
            raise DatabaseError(f"Data integrity issue: multiple users found for identificator {user_identificator}.")
        except SQLAlchemyError as e:
            logger.error(f"Database error finding user by identificator {user_identificator}: {e}", exc_info=True)
            raise DatabaseError(f"Error accessing user data for identificator {user_identificator}.")


    def add(self, project: Project) -> None:
        logger.debug(f"Repository: Attempting to add project '{project.title}' for user '{project.user_identificator}'")
        try:
            user_db = self._find_user_db_by_identificator(project.user_identificator)
            if not user_db:
                logger.error(f"Repository: User with identificator {project.user_identificator} not found. Cannot add project '{project.title}'.")
                raise UserNotFoundError(user_identificator=project.user_identificator)

            project_db = project.to_orm()
            project_db.user_id = user_db.id 

            self._session.add(project_db)
            self._session.flush() 
            logger.info(f"Repository: Project '{project.title}' (ID: {project.identificator}) added and flushed to session for user ID {user_db.id}.")

        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Repository: Database error adding/flushing project '{project.title}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to add project '{project.title}' to the database session.")
        except UserNotFoundError: 
             raise
        except Exception as e:
             logger.error(f"Repository: Unexpected error adding project '{project.title}': {e}", exc_info=True)
             raise DatabaseError(f"An unexpected error occurred while adding project '{project.title}'.")

    def get_all_by_user(self, user_identificator: str) -> List[Project]:
        logger.debug(f"Repository: Attempting to get all projects for user '{user_identificator}'")
        try:
            stmt = (
                select(ProjectDB)
                .join(ProjectDB.user)
                .where(UserDB.identificator == user_identificator)
                .options(joinedload(ProjectDB.user)) # Eager load user for from_orm
                .order_by(ProjectDB.title)
            )
            projects_db = self._session.execute(stmt).scalars().all()

            logger.info(f"Repository: Found {len(projects_db)} projects for user '{user_identificator}'.")
            return [Project.from_orm(p) for p in projects_db]

        except SQLAlchemyError as e:
            logger.error(f"Repository: Database error getting all projects for user '{user_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Error retrieving projects for user '{user_identificator}'.")
        except ValueError as e:
             logger.error(f"Repository: Error converting ProjectDB to Project during get_all_by_user for user '{user_identificator}': {e}", exc_info=True)
             raise DatabaseError(f"Error processing project data for user '{user_identificator}'.")
        
    def get_projects_with_focus_sessions_by_user(self, user_identificator: str) -> List[ProjectDB]:
        logger.debug(f"Repository: Getting projects with focus sessions for user '{user_identificator}'")
        try:
            stmt = (
                select(ProjectDB)
                .join(ProjectDB.user)
                .where(UserDB.identificator == user_identificator)
                .options(
                    joinedload(ProjectDB.user),
                    joinedload(ProjectDB.focus_sessions)
                )
                .order_by(ProjectDB.title)
            )
            projects_db = self._session.execute(stmt).unique().scalars().all()
            logger.info(f"Repository: Found {len(projects_db)} projects with focus sessions for user '{user_identificator}'.")
            return projects_db
        except SQLAlchemyError as e:
            logger.error(f"Repository: DB error getting projects/sessions for user '{user_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Error retrieving project/session data for user '{user_identificator}'.")
        except Exception as e:
            logger.error(f"Repository: Unexpected error getting projects/sessions for user '{user_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while retrieving project/session data for user '{user_identificator}'.")

    def get_by_id(self, project_identificator: str, user_identificator: str) -> ProjectDetailsDTO:
        logger.debug(f"Repository: Attempting to get project details by id '{project_identificator}' for user '{user_identificator}'")
        result_dto = ProjectDetailsDTO()

        try:
            stmt = (
                select(ProjectDB)
                .join(ProjectDB.user)
                .where(ProjectDB.identificator == project_identificator)
                .where(UserDB.identificator == user_identificator)
                .options(
                    joinedload(ProjectDB.user), # Necessário para Project.from_orm
                    joinedload(ProjectDB.tasks).joinedload(TaskDB.status), # Carrega tarefas e seus status
                    joinedload(ProjectDB.focus_sessions) # Carrega sessões de foco
                )
            )

            project_db = self._session.execute(stmt).unique().scalar_one_or_none()

            if not project_db:
                logger.warning(f"Repository: Project with id '{project_identificator}' not found for user '{user_identificator}'.")
                return result_dto # Retorna DTO vazio se o projeto não for encontrado

            logger.info(f"Repository: Project '{project_db.title}' (ID: {project_identificator}) found for user '{user_identificator}'. Processing details...")

            try:
                result_dto.project = Project.from_orm(project_db)
            except ValueError as e:
                logger.error(f"Repository: Error converting ProjectDB to Project for id '{project_identificator}': {e}", exc_info=True)
                # Considerar se deve retornar DTO parcial ou levantar erro
                raise DatabaseError(f"Error processing project data for project '{project_identificator}'.")

            # 2. Converte as Tarefas para o modelo de domínio
            if project_db.tasks:
                logger.debug(f"Repository: Converting {len(project_db.tasks)} tasks for project '{result_dto.project.title}'.")
                for task_db in project_db.tasks:
                    try:
                        task_domain = Task.from_orm(task_db)
                        if task_domain:
                            result_dto.tasks.append(task_domain)
                        else:
                             logger.warning(f"Repository: Task.from_orm returned None for TaskDB id {task_db.id}")
                    except Exception as e:
                        logger.error(f"Repository: Failed to convert TaskDB id {task_db.id} to domain model: {e}", exc_info=True)
                        # Considerar adicionar uma nota de erro ao DTO ou levantar exceção dependendo da política de erro
            else:
                 logger.debug(f"Repository: No tasks found/loaded for project '{result_dto.project.title}'.")


            if project_db.focus_sessions:
                logger.debug(f"Repository: Converting {len(project_db.focus_sessions)} focus sessions for project '{result_dto.project.title}'.")
                for session_db in project_db.focus_sessions:
                    try:
                        session_domain = FocusSession.from_orm(session_db)
                        if session_domain:
                            result_dto.focus_sessions.append(session_domain)
                        else:
                            logger.warning(f"Repository: FocusSession.from_orm returned None for FocusSessionDB id {session_db.id}")
                    except Exception as e:
                        logger.error(f"Repository: Failed to convert FocusSessionDB id {session_db.id} to domain model: {e}", exc_info=True)
                        # Considerar adicionar uma nota de erro ao DTO ou levantar exceção
            else:
                 logger.debug(f"Repository: No focus sessions found/loaded for project '{result_dto.project.title}'.")


            # Retorna o DTO preenchido
            return result_dto

        except MultipleResultsFound:
             logger.error(f"Database integrity error: Multiple projects found for id {project_identificator} and user {user_identificator}")
             raise DatabaseError(f"Data integrity issue: multiple projects found for id {project_identificator}.")
        except SQLAlchemyError as e:
            logger.error(f"Repository: Database error getting project details by id '{project_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Error retrieving details for project with id '{project_identificator}'.")
        except Exception as e:
            # Captura outros erros inesperados (incluindo potenciais erros de conversão não pegos antes)
            logger.error(f"Repository: Unexpected error getting project details by id '{project_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while retrieving details for project '{project_identificator}'.")


    # Não revisei ainda ========================


    def update(self, project: Project) -> None:
        """
        Updates an existing project in the database session and flushes.

        Args:
            project: The Project domain model instance with updated data.

        Raises:
            ProjectNotFoundError: If the project to update is not found for the specified user.
            DatabaseError: If a database error occurs during find or flush.
        """
        logger.debug(f"Repository: Attempting to find project for update: id '{project.identificator}' for user '{project.user_identificator}'")
        try:
            # Find the existing ProjectDB entity using select and scalar_one_or_none
            stmt = (
                 select(ProjectDB)
                .join(ProjectDB.user)
                .where(ProjectDB.identificator == project.identificator)
                .where(UserDB.identificator == project.user_identificator)
            )
            project_db = self._session.execute(stmt).scalar_one_or_none() # Use _or_none

            if not project_db:
                 logger.warning(f"Repository: Project with id '{project.identificator}' not found for update for user '{project.user_identificator}'.")
                 raise ProjectNotFoundError(project_id=project.identificator) # Raise if not found for update

            # Update attributes from the domain model onto the managed ORM instance
            project_db.title = project.title
            project_db.color = project.color
            project_db.active = project.active

            self._session.add(project_db) # Ensure it's marked dirty
            self._session.flush() # Flush changes
            logger.info(f"Repository: Project '{project.title}' (ID: {project.identificator}) updated and flushed in session.")

        except ProjectNotFoundError: # Re-raise specific error
            raise
        except MultipleResultsFound: # Should ideally not happen with identificator+user filter
             logger.error(f"Database integrity error: Multiple projects found for update: id {project.identificator} and user {project.user_identificator}")
             raise DatabaseError(f"Data integrity issue: multiple projects found for update: id {project.identificator}.")
        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Repository: Database error preparing/flushing project update for id '{project.identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to update project with id '{project.identificator}'.")
        except Exception as e:
             logger.error(f"Repository: Unexpected error updating project '{project.identificator}': {e}", exc_info=True)
             raise DatabaseError(f"An unexpected error occurred while updating project '{project.identificator}'.")


    def delete(self, project_identificator: str, user_identificator: str) -> bool:
        """
        Marks a project for deletion in the database session and flushes.

        Args:
            project_identificator: The UUID string of the project to delete.
            user_identificator: The UUID string of the user owning the project.

        Returns:
            True if the project was found and marked for deletion, False otherwise.

        Raises:
            DatabaseError: If a database error occurs during find or flush.
        """
        logger.debug(f"Repository: Attempting to find project for deletion: id '{project_identificator}' for user '{user_identificator}'")
        try:
            stmt = (
                 select(ProjectDB)
                .join(ProjectDB.user)
                .where(ProjectDB.identificator == project_identificator)
                .where(UserDB.identificator == user_identificator)
            )
            project_db = self._session.execute(stmt).scalar_one_or_none() # Use _or_none

            if project_db:
                logger.info(f"Repository: Found project '{project_db.title}' (ID: {project_identificator}) for deletion.")
                self._session.delete(project_db)
                self._session.flush() # Flush deletion
                logger.info(f"Repository: Project '{project_db.title}' (ID: {project_identificator}) marked for deletion and flushed in session.")
                return True
            else:
                logger.warning(f"Repository: Project with id '{project_identificator}' not found for deletion for user '{user_identificator}'.")
                return False # Return False if not found, matching UserRepository

        except MultipleResultsFound: # Should ideally not happen
            logger.error(f"Database integrity error: Multiple projects found for deletion: id {project_identificator} and user {user_identificator}")
            raise DatabaseError(f"Data integrity issue: multiple projects found for deletion: id {project_identificator}.")
        except (SQLAlchemyError, IntegrityError) as e: # Catch potential errors during delete/flush (e.g., FK constraints if cascade isn't set right)
            logger.error(f"Repository: Database error preparing/flushing project deletion for id '{project_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to delete project with id '{project_identificator}'.")
        except Exception as e:
            logger.error(f"Repository: Unexpected error deleting project '{project_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while deleting project '{project_identificator}'.")


  
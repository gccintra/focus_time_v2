from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, MultipleResultsFound 

from app.infra.db import db
from app.infra.entities.task_db import TaskDB
from app.infra.entities.project_db import ProjectDB
from app.infra.entities.task_status_db import TaskStatusDB
from app.infra.entities.user_db import UserDB # Import UserDB if needed for joins/filters
from app.models.task import Task
from app.models.exceptions import DatabaseError, ProjectNotFoundError, TaskNotFoundError, TaskStatusNotFound # Assuming TaskNotFoundError exists
from app.utils.logger import logger

class TaskRepository:
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
        
    def _find_status_db_by_id(self, status_id: int) -> Optional[TaskStatusDB]:
        """Finds a task status DB entity by its primary key ID."""
        logger.debug(f"Repository: Finding TaskStatusDB by id '{status_id}'")
        if status_id is None: 
            logger.error("Repository: Cannot find status with None ID.")
            return None
        try:
            stmt = select(TaskStatusDB).where(TaskStatusDB.id == status_id)
            status_db = self._session.execute(stmt).scalar_one_or_none()
            if status_db:
                logger.debug(f"Repository: TaskStatusDB found for id '{status_id}' (Name: {status_db.name})")
            else:
                logger.debug(f"Repository: TaskStatusDB not found for id '{status_id}'")
            return status_db
        except MultipleResultsFound: # Should not happen if id is PK
            logger.error(f"Database integrity error: Multiple TaskStatus found with id '{status_id}'")
            raise DatabaseError(f"Data integrity issue: multiple statuses found for id '{status_id}'.")
        except SQLAlchemyError as e:
            logger.error(f"Repository: Database error finding TaskStatusDB by id '{status_id}': {e}", exc_info=True)
            raise DatabaseError(f"Error accessing database while finding status id '{status_id}'.")
        except Exception as e:
            logger.error(f"Repository: Unexpected error finding TaskStatusDB by id '{status_id}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while finding status id '{status_id}'.")
        

    def add(self, task_domain: Task) -> TaskDB:
        logger.debug(f"Repository: Adding new Task '{task_domain.title}' for Project ID {task_domain.project.identificator} to session")
        try:

            project_db = self._find_project_db_by_identificator(task_domain.project.identificator)
            if not project_db:
                logger.error(f"Repository: Project with identificator {task_domain.project.identificator} not found. Cannot add Task.")
                raise ProjectNotFoundError(project_id=task_domain.project.identificator)
            
            status_db = self._find_status_db_by_id(task_domain.status.id)
            if not status_db:
                logger.error(f"Repository: Task Status with identificator {task_domain.status.id} not found. Cannot add Task")
                raise TaskStatusNotFound(task_status_id=task_domain.status.id)
            
            task_db = task_domain.to_orm()

            # Associate with Project and Status ORM entities
            # SQLAlchemy handles setting the foreign keys (project_id, status_id)
            # based on these relationships when flushed/committed.
            # task_db.project = project_db # Assign the ORM object
            # task_db.status = status_db   # Assign the ORM object
            # Or alternatively, if relationships aren't set up or you prefer explicit FKs:
            task_db.project_id = project_db.id
            task_db.status_id = status_db.id

            self._session.add(task_db)
            self._session.flush() 
            logger.info(f"Repository: Task '{task_db.title}' (ID: {task_db.identificator}) added/flushed successfully.")
            return task_db
        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Repository: Database error adding/flushing Task '{task_domain.title}': {e}", exc_info=True)
            raise DatabaseError(f"Error saving task '{task_domain.title}' to database session.")
        except (ProjectNotFoundError, TaskStatusNotFound): 
            raise
        except Exception as e:
            logger.error(f"Repository: Unexpected error adding Task '{task_domain.title}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while adding task '{task_domain.title}'.")
        

    def find_by_identificator(self, task_identificator: str, load_relations: bool = True) -> Optional[TaskDB]:
        logger.debug(f"Repository: Finding TaskDB by identificator '{task_identificator}' (load_relations={load_relations})")
        try:
            stmt = select(TaskDB).where(TaskDB.identificator == task_identificator)

            if load_relations:
                stmt = stmt.options(
                    joinedload(TaskDB.project).joinedload(ProjectDB.user), 
                    joinedload(TaskDB.status)
                )

            # Use unique() before scalar_one_or_none if joins might produce duplicate TaskDB rows
            task_db = self._session.execute(stmt).unique().scalar_one_or_none()

            if not task_db:
                logger.warning(f"Repository: Task with identificator '{task_identificator}' not found.")
                return None

            logger.debug(f"Repository: Task found for identificator '{task_identificator}' (Title: {task_db.title})")
            if load_relations and (not task_db.project or not task_db.status):
                logger.warning(f"Repository: Relationships not fully loaded for Task '{task_identificator}', despite request.")

            return task_db
        except MultipleResultsFound: 
             logger.error(f"Database integrity error: Multiple Tasks found with identificator '{task_identificator}'")
             raise DatabaseError(f"Data integrity issue: multiple tasks found for identificator '{task_identificator}'.")
        except SQLAlchemyError as e:
            logger.error(f"Repository: Database error finding TaskDB by identificator '{task_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Error accessing database while finding task '{task_identificator}'.")
        except Exception as e:
             logger.error(f"Repository: Unexpected error finding TaskDB by identificator '{task_identificator}': {e}", exc_info=True)
             raise DatabaseError(f"An unexpected error occurred while finding task '{task_identificator}'.")
        

    def update(self, task_domain: Task) -> TaskDB:
        logger.debug(f"Repository: Updating Task with identificator '{task_domain.identificator}'")
        try:
   
            # We don't necessarily need to load relations just to update fields,
            # unless the update logic itself depends on them.
            stmt = select(TaskDB).where(TaskDB.identificator == task_domain.identificator)
            task_db = self._session.execute(stmt).scalar_one_or_none()

            if not task_db:
                logger.error(f"Repository: Task with identificator '{task_domain.identificator}' not found for update.")
                raise TaskNotFoundError(task_id=task_domain.identificator)

            new_status_db = self._find_status_db_by_id(task_domain.status.id)
            if not new_status_db:
                logger.error(f"Repository: New Task Status with ID {task_domain.status.id} not found. Cannot update Task '{task_domain.identificator}'.")
                raise TaskStatusNotFound(task_status_id=task_domain.status.id)

  
            # Only update fields that are expected to change.
            task_db.title = task_domain.title
            task_db.description = task_domain.description
            task_db.completed_at = task_domain.completed_at
            task_db.status_id = new_status_db.id # Assign the foreign key ID

            # INTERESSANTE!!!!

            # Optional: Update project if allowed (be cautious about implications)
            # if task_domain.project and task_db.project.identificator != task_domain.project.identificator:
            #     new_project_db = self._find_project_db_by_identificator(task_domain.project.identificator)
            #     if not new_project_db:
            #         raise ProjectNotFoundError(project_id=task_domain.project.identificator)
            #     task_db.project_id = new_project_db.id

            # Optional: Manually update 'updated_at' if not handled automatically by DB/SQLAlchemy
            # task_db.updated_at = datetime.utcnow() # Requires 'from datetime import datetime'

         
            self._session.flush()

            logger.info(f"Repository: Task '{task_db.title}' (Identificator: {task_db.identificator}) updated and flushed successfully.")
            return task_db

        except (TaskNotFoundError, TaskStatusNotFound, ProjectNotFoundError): 
            raise
        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Repository: Database error updating Task '{task_domain.identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Error updating task '{task_domain.identificator}' in database.")
        except Exception as e:
            logger.error(f"Repository: Unexpected error updating Task '{task_domain.identificator}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while updating task '{task_domain.identificator}'.")
        


    def delete(self, task: Task) -> None:
        logger.debug(f"Repository: Deleting Task with identificator '{task.identificator}'")

        try:
            stmt = delete(TaskDB).where(TaskDB.identificator == task.identificator)
            result = self._session.execute(stmt)

            # Verifica se a task existia, mesmo que a service ja tenha verificado
            if result.rowcount == 0:
               logger.warning(f"No task found with identificator '{task.identificator}' to delete.")
               raise TaskNotFoundError(task_id=str(task.identificator)) 

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(f"Database error deleting task '{task.identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Database error deleting task '{task.identificator}': {e}") from e
        except Exception as e:
            self._session.rollback()
            logger.error(f"Unexpected error deleting task '{task.identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Unexpected error deleting task '{task.identificator}': {e}") from e
        

      # ===========================================


        
    def get_all_by_project_id(self, project_identificator: str, load_relations: bool = True) -> List[TaskDB]:
        """Retrieves all tasks associated with a specific project identificator using SQLAlchemy 2.0 syntax."""
        logger.debug(f"Repository: Getting all tasks for project identificator '{project_identificator}' (load_relations={load_relations})")
        try:
            stmt = (
                select(TaskDB)
                .join(TaskDB.project) # Join TaskDB with ProjectDB
                .where(ProjectDB.identificator == project_identificator) # Filter on ProjectDB's identificator
            )

            if load_relations:
                stmt = stmt.options(
                    # Eager load project (and its user) and status for each task
                    joinedload(TaskDB.project).joinedload(ProjectDB.user),
                    joinedload(TaskDB.status)
                )

            # Example ordering
            stmt = stmt.order_by(TaskDB.created_at.desc())

            # Use unique().scalars().all() because joins might create duplicate TaskDB rows before unique()
            tasks_db = self._session.execute(stmt).unique().scalars().all()

            logger.info(f"Repository: Found {len(tasks_db)} tasks for project '{project_identificator}'.")
            return tasks_db

        except SQLAlchemyError as e:
            logger.error(f"Repository: Database error getting tasks for project '{project_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"Error retrieving tasks for project '{project_identificator}'.")
        except Exception as e:
            logger.error(f"Repository: Unexpected error getting tasks for project '{project_identificator}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while retrieving tasks for project '{project_identificator}'.")
        






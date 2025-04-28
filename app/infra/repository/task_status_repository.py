from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, MultipleResultsFound 

from app.infra.db import db
from app.infra.entities.task_status_db import TaskStatusDB
from app.models.task_status import TaskStatus
from app.models.exceptions import DatabaseError, TaskStatusNotFound 
from app.utils.logger import logger



class TaskStatusRepository:
    def __init__(self, session: Session = db.session):
        self._session = session

    def find_by_name(self, name: str) -> Optional[TaskStatusDB]:
        logger.debug(f"Repository: Finding TaskStatusDB by name '{name}'")
        try:
            stmt = select(TaskStatusDB).where(TaskStatusDB.name == name)
            status_db = self._session.execute(stmt).scalar_one_or_none()
            if status_db:
                logger.debug(f"Repository: TaskStatusDB found for name '{name}' (ID: {status_db.id})")
            else:
                logger.debug(f"Repository: TaskStatusDB not found for name '{name}'")
            return status_db
        except MultipleResultsFound: # Should not happen if name is unique, but good practice
            logger.error(f"Database integrity error: Multiple TaskStatus found with name '{name}'")
            raise DatabaseError(f"Data integrity issue: multiple statuses found for name '{name}'.")
        except SQLAlchemyError as e:
            logger.error(f"Repository: Database error finding TaskStatusDB by name '{name}': {e}", exc_info=True)
            raise DatabaseError(f"Error accessing database while finding status '{name}'.")
        except Exception as e:
             logger.error(f"Repository: Unexpected error finding TaskStatusDB by name '{name}': {e}", exc_info=True)
             raise DatabaseError(f"An unexpected error occurred while finding status '{name}'.")

    def find_by_id(self, status_id: int) -> Optional[TaskStatusDB]:
        logger.debug(f"Repository: Finding TaskStatusDB by id '{status_id}'")
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

    def get_default_status(self) -> TaskStatusDB:
        default_status_name = "in progress"
        logger.debug(f"Repository: Getting default TaskStatusDB ('{default_status_name}')")
        try:
            status_db = self.find_by_name(default_status_name) 
            if not status_db:
                logger.error(f"Repository: Default task status '{default_status_name}' not found in the database.")
                raise TaskStatusNotFound()
            return status_db
        except TaskStatusNotFound: 
            raise
        except DatabaseError as e: 
            logger.error(f"Repository: Database error fetching default task status: {e}", exc_info=True)
            raise #
        except Exception as e:
            logger.error(f"Repository: Unexpected error fetching default task status: {e}", exc_info=True)
            raise DatabaseError("An unexpected error occurred while fetching the default task status.")
        

    # Melhorar exceção aqui
    def get_completed_status(self) -> TaskStatusDB:
        completed_status_name = "completed"
        logger.debug(f"Repository: Getting completed TaskStatusDB ('{completed_status_name}')")
        try:
            status_db = self.find_by_name(completed_status_name)
            if not status_db:
                logger.error(f"Repository: Completed task status '{completed_status_name}' not found in the database.")
                raise TaskStatusNotFound()
            return status_db
        except TaskStatusNotFound:
            raise
        except DatabaseError as e:
            logger.error(f"Repository: Database error fetching completed task status: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Repository: Unexpected error fetching completed task status: {e}", exc_info=True)
            raise DatabaseError("An unexpected error occurred while fetching the completed task status.")



    def add(self, status_domain: TaskStatus) -> TaskStatusDB:
        """Adds a new task status to the database session and flushes."""
        logger.debug(f"Repository: Adding new TaskStatus '{status_domain.name}' to session")
        try:
            # Convert domain to ORM entity using the model's method
            status_db = status_domain.to_orm()
            self._session.add(status_db)
            self._session.flush() # Use flush to get the ID and catch potential errors early
            logger.info(f"Repository: TaskStatus '{status_db.name}' added/flushed with ID {status_db.id}")
            return status_db
        except (SQLAlchemyError, IntegrityError) as e: # Catch specific DB errors
            logger.error(f"Repository: Database error adding/flushing TaskStatus '{status_domain.name}': {e}", exc_info=True)
            # DO NOT rollback here, service layer handles transactions
            raise DatabaseError(f"Error saving task status '{status_domain.name}' to database session.")
        except Exception as e:
            logger.error(f"Repository: Unexpected error adding TaskStatus '{status_domain.name}': {e}", exc_info=True)
            # DO NOT rollback here
            raise DatabaseError(f"An unexpected error occurred while adding task status '{status_domain.name}'.")

    # Add other methods like list_all, update, delete as needed following the same pattern

#from ..models.task import ToDo
#from ..models.exceptions import TaskValidationError, TaskNotFoundError
from multiprocessing import Value
from typing import Dict, Optional

from sqlalchemy import Boolean
from app.infra.entities.project_db import ProjectDB
from app.infra.repository.project_repository import ProjectRepository
from app.infra.repository.task_status_repository import TaskStatusRepository
from app.models.project import Project
from app.models.task import Task
from app.models.task_status import TaskStatus
from ..infra.repository.task_repository import TaskRepository
from datetime import datetime
from ..utils.logger import logger
from ..models.exceptions import AuthorizationError, DatabaseError, ProjectNotFoundError, TaskNotFoundError, TaskStatusNotFound, TaskValidationError

class TaskService:
    def __init__(self):
        self.project_repo = ProjectRepository()
        self.task_status_repo = TaskStatusRepository()
        self.repo = TaskRepository()

        
    def create_task(self, user_id: str, project_id: str, title: str, description: str = None) -> Task:
        logger.info(f"Service: Attempting to save focus session for project '{project_id}' by user '{user_id}'")

        try:
            project_db_check = self._verify_project_and_authorization(user_id=user_id, project_id=project_id)
            
            try:
                project_domain = Project.from_orm(project_db_check)
                if not project_domain: 
                    raise ValueError("Failed to convert found ProjectDB to domain object.")
            except ValueError as e:
                logger.error(f"Service: Error converting ProjectDB to Project domain object for id '{project_id}': {e}", exc_info=True)
                raise DatabaseError(f"Error processing project data for project '{project_id}'.")
            
            try:
                default_status_db = self.task_status_repo.get_default_status()
            except TaskStatusNotFound as e:
                logger.critical(f"Service: Default task status not found in DB: {e}", exc_info=True)
                raise 
            except DatabaseError as e:
                logger.error(f"Service: Database error fetching default task status: {e}", exc_info=True)
                raise 
            
            try:
                default_status_domain = TaskStatus.from_orm(default_status_db)
                if not default_status_domain:
                    raise ValueError("Conversion from TaskStatusDB to TaskStatus domain returned None.")
            except (ValueError, DatabaseError) as e:
                logger.error(f"Service: Error converting default TaskStatusDB to domain: {e}", exc_info=True)
                raise DatabaseError("Error processing default task status data.")
            
            try:
                new_task = Task(
                    title=title,
                    description=description,
                    project=project_domain,
                    status=default_status_domain
                )
            except TaskValidationError as e:
                logger.warning(f"Service: Task validation failed during creation: {e}")
                raise 
                
            
            self.repo.add(new_task)
            self.repo._session.commit() 

            logger.info(f"Service: Task (Domain ID: {new_task.identificator}) saved successfully for project '{project_id}' by user '{user_id}'")
            return new_task

        except (ProjectNotFoundError, TaskStatusNotFound) as e:
            logger.error(f"Service: Failed to create task due to missing dependency: {e}", exc_info=True)
            self.repo._session.rollback() 
            raise 
        except (AuthorizationError, TaskValidationError, DatabaseError) as e:
            logger.error(f"Service: Error during task creation transaction: {e}", exc_info=True)
            self.repo._session.rollback() 
            raise 
        except Exception as e:
            logger.error(f"Service: Unexpected error during task creation transaction: {e}", exc_info=True)
            try:
                self.repo._session.rollback() 
            except Exception as rb_ex:
                logger.error(f"Service: Exception during rollback after unexpected error: {rb_ex}", exc_info=True)
            raise DatabaseError("An unexpected internal error occurred during task creation.") from e
        



    def change_task_status(self, user_id: str, project_id: str, task_id: str, target_status_name: str) -> Task:
        logger.info(f"Service: Attempting to update task '{task_id}' to status '{target_status_name}' for project '{project_id}' by user '{user_id}'")
        try:
            self._verify_project_and_authorization(user_id=user_id, project_id=project_id)
            
            task_db = self.repo.find_by_identificator(task_identificator=task_id, load_relations=False)

            if task_db is None:
                logger.warning(f"Service: Task '{task_id}' not found in project '{project_id}'.")
                raise TaskNotFoundError(task_id=task_id) 
            
            try:
                task_domain = Task.from_orm(task_db=task_db)
            except ValueError as e:
                logger.error(f"Service: Error converting TaskDB to Task domain object for id '{task_id}': {e}", exc_info=True)
                raise DatabaseError(f"Error processing task data for task '{task_id}'.") from e
 
            if target_status_name == "completed":
                try:
                    new_status_db = self.task_status_repo.get_completed_status()
                    new_status_domain = TaskStatus.from_orm(new_status_db)
                    if not new_status_domain: raise ValueError("Conversion from completed TaskStatusDB returned None.")
                    task_domain.complete(new_status_domain)
                except TaskStatusNotFound as e:
                    logger.critical(f"Service: 'Completed' task status not found in DB: {e}", exc_info=True)
                    raise
                except TaskValidationError as e:
                    logger.error(f"Service: Task validation failed during completion: {e}")
                    raise 
                except (DatabaseError, ValueError) as e:
                    logger.error(f"Service: Error processing 'completed' status data: {e}", exc_info=True)
                    raise DatabaseError("Error processing 'completed' task status data.") from e 
    
            elif target_status_name == "in progress":  
                try:
                    new_status_db = self.task_status_repo.get_default_status()
                    new_status_domain = TaskStatus.from_orm(new_status_db)
                    if not new_status_domain: raise ValueError("Conversion from default TaskStatusDB returned None.")
                    task_domain.reopen(new_status_domain)
                except TaskStatusNotFound as e:
                    logger.critical(f"Service: 'Default' task status not found in DB: {e}", exc_info=True)
                    raise 
                except TaskValidationError as e: 
                    logger.error(f"Service: Task validation failed during reopening: {e}")
                    raise 
                except (ValueError, DatabaseError) as e: 
                    logger.error(f"Service: Error processing 'default' status data: {e}", exc_info=True)
                    raise DatabaseError("Error processing 'default' task status data.") from e
                
            else:
                logger.warning(f"Service: Invalid target status name provided: '{target_status_name}' for task '{task_id}'.")
                raise ValueError(f"Invalid target status name: '{target_status_name}'. Allowed values are 'completed' or 'reopen'.")
               
            self.repo.update(task_domain)
            self.repo._session.commit()
            logger.info(f"Service: Task (Domain ID: {task_domain.identificator}) status updated to '{task_domain.status.name}' successfully.")
            return task_domain
        
        except (ProjectNotFoundError, AuthorizationError, TaskNotFoundError, TaskStatusNotFound, TaskValidationError, ValueError, DatabaseError) as e:
            logger.error(f"Service: Failed to change task status for task '{task_id}'. Reason: {type(e).__name__} - {e}", exc_info=True)
            self.repo._session.rollback() 
            raise 

        except Exception as e:
            logger.error(f"Service: Unexpected error changing task status for task '{task_id}': {e}", exc_info=True)
            try:
                self.repo._session.rollback() 
            except Exception as rb_ex:
                logger.error(f"Service: Exception during rollback after unexpected error: {rb_ex}", exc_info=True)
            raise DatabaseError("An unexpected internal error occurred while updating task status.") from e
        

    def delete_task(self, user_id: str, project_id: str, task_id: str) -> None:
        logger.info(f"Service: Attempting to delete task '{task_id}' in project '{project_id}' by user '{user_id}'")
        try:
            self._verify_project_and_authorization(user_id=user_id, project_id=project_id)

            task_db = self.repo.find_by_identificator(task_identificator=task_id, load_relations=False)
            if task_db is None:
                logger.warning(f"Service: Task '{task_id}' not found for deletion in project '{project_id}'.")
                raise TaskNotFoundError(task_id=task_id)
        
            try:
                task_domain = Task.from_orm(task_db)
            except ValueError as e:
                logger.error(f"Service: Error converting TaskDB to Task domain object for id '{task_id}': {e}", exc_info=True)
                raise DatabaseError(f"Error processing task data for task '{task_id}'.") from e
            
            if task_domain.project is None or task_domain.project.identificator != project_id:
                logger.error(f"Service: Task '{task_id}' found but does not belong to project '{project_id}'. Aborting deletion.")
                raise AuthorizationError(user_id=user_id, resource_id=task_id, message="Task does not belong to the specified project.")

            self.repo.delete(task_domain)

            self.repo._session.commit()
            logger.info(f"Service: Task (Domain ID: {task_domain.identificator}) deleted successfully.")

        except (ProjectNotFoundError, AuthorizationError, TaskNotFoundError) as e:
            logger.warning(f"Service: Failed to delete task '{task_id}'. Reason: {type(e).__name__} - {e}")
            self.repo._session.rollback()
            raise 

        except DatabaseError as e:
            logger.error(f"Service: Database error during task deletion for task '{task_id}': {e}", exc_info=True)
            self.repo._session.rollback()
            raise 

        except Exception as e:
            logger.error(f"Service: Unexpected error deleting task '{task_id}': {e}", exc_info=True)
            try:
                self.repo._session.rollback()
            except Exception as rb_ex:
                logger.error(f"Service: Exception during rollback after unexpected error: {rb_ex}", exc_info=True)
            raise DatabaseError("An unexpected internal error occurred while deleting the task.") from e


    def _verify_project_and_authorization(self, user_id: str, project_id: str) -> ProjectDB:
        project_db_check =  self.project_repo.find_by_id_with_user(project_identificator=project_id)

        if project_db_check is None:
            logger.warning(f"Service: Project '{project_id}' not found during verification.")
            raise ProjectNotFoundError(project_id=project_id)

        if project_db_check.user is None or project_db_check.user.identificator != user_id:
            owner_id = project_db_check.user.identificator if project_db_check.user else "unknown"
            logger.error(f"Service: Authorization failed. User '{user_id}' attempted action on project '{project_id}' owned by '{owner_id}'.")
            raise AuthorizationError(user_id=user_id, resource_id=project_id, message="User does not own this project.")

        return project_db_check
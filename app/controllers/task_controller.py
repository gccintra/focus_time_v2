from pydoc import describe
from flask import jsonify, render_template, abort
from app.services.task_service import TaskService
from ..models.exceptions import AuthorizationError, DatabaseError, ProjectNotFoundError, TaskStatusNotFound, TaskValidationError, TaskNotFoundError
from ..utils.logger import logger

class TaskController:
    def __init__(self):
        self.service = TaskService()
        
    def create_task(self, user_id, project_id, data):
        title = data.get('title')
        if not title:
            raise ValueError("Missing 'title' field in request data.")
        description = data.get('description') if data.get('description') else None
        try:        
            new_task = self.service.create_task(
                user_id=user_id, 
                project_id=project_id, 
                title=title, 
                description=description
            )

            return jsonify({
                "success": True,
                "message": "Task created successfully",
                "data": {
                    "id": new_task.identificator,
                    "title": new_task.title,
                    "created_at": new_task.created_at,
                    "status": new_task.status.name
                },
                "error": None
            }), 201
        
        except ProjectNotFoundError as e:
            error_type = type(e).__name__ 
            logger.warning(f"Controller: Resource not found during creating task for project '{project_id}'. {error_type}: {e}")
            return jsonify({
                "success": False,
                "message": str(e), 
                "data": None,
                "error": {
                    "code": 404,
                    "type": type(e).__name__,
                    "details": str(e)
                }
            }), 404
        
        except AuthorizationError as e:
            logger.warning(f"Controller: Authorization failed for user '{user_id}' on project '{project_id}'. {e}")
            return jsonify({
                "success": False,
                "message": "Authorization failed. You do not have permission to perform this action.",
                "data": None,
                "error": {
                    "code": 403,
                    "type": "AuthorizationError",
                    "details": str(e)
                }
            }), 403

        except (TaskStatusNotFound, DatabaseError) as e:
            error_type = type(e).__name__ 
            logger.error(f"Controller: Internal server error during creating task for project '{project_id}'. {error_type}: {e}", exc_info=True)
            user_message = "An internal server error occurred. Please try again later or contact support."
            if isinstance(e, TaskStatusNotFound):
                user_message = "An internal configuration error occurred. Please contact support."

            return jsonify({
                "success": False,
                "message": user_message,
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError", 
                    "details": f"Internal error of type: {error_type}" 
                }
            }), 500
        
        except TaskValidationError as e:
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {
                    "code": 400,
                    "type": "TaskValidationError",
                    "details": str(e)
                }
            }), 400
        
        except Exception as e:
            logger.error(f"Erro ao criar task para o projeto {project_id}: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Something went wrong. Please try again later.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "details": "An unexpected error occurred."
                }
            }), 500
        

    def change_task_status(self, user_id: str, project_id: str, task_id: str, data: dict):
        try:
            target_status_name = data.get('status')
            if not target_status_name:
                raise ValueError("Missing 'status' field in request data.")

            updated_task = self.service.change_task_status(
                user_id=user_id,
                project_id=project_id,
                task_id=task_id,
                target_status_name=target_status_name 
            )

            return jsonify({
                "success": True,
                "message": "Task status changed successfully.",
                "data": {
                    "status": updated_task.status.name,
                    "created_at": updated_task.created_at if updated_task.created_at else None,
                    "completed_at": updated_task.completed_at if updated_task.completed_at else None
                },
                "error": None
            }), 200


        except (ProjectNotFoundError, TaskNotFoundError) as e:
            error_type = type(e).__name__ 
            logger.warning(f"Controller: Resource not found during task status change for task '{task_id}'. {error_type}: {e}")
            return jsonify({
                "success": False,
                "message": str(e), 
                "data": None,
                "error": {
                    "code": 404,
                    "type": type(e).__name__,
                    "details": str(e)
                }
            }), 404

        except AuthorizationError as e:
            logger.warning(f"Controller: Authorization failed for user '{user_id}' on task '{task_id}'. {e}")
            return jsonify({
                "success": False,
                "message": "Authorization failed. You do not have permission to perform this action.",
                "data": None,
                "error": {
                    "code": 403,
                    "type": "AuthorizationError",
                    "details": str(e)
                }
            }), 403

        except (TaskValidationError, ValueError) as e:
            error_type = type(e).__name__ 
            logger.warning(f"Controller: Validation error during task status change for task '{task_id}'. {error_type}: {e}")
            return jsonify({
                "success": False,
                "message": str(e), 
                "data": None,
                "error": {
                    "code": 400,
                    "type": type(e).__name__, 
                    "details": str(e)
                }
            }), 400

        except (TaskStatusNotFound, DatabaseError) as e:
            error_type = type(e).__name__ 
            logger.error(f"Controller: Internal server error during task status change for task '{task_id}'. {error_type}: {e}", exc_info=True)
            user_message = "An internal server error occurred. Please try again later or contact support."
            if isinstance(e, TaskStatusNotFound):
                user_message = "An internal configuration error occurred. Please contact support."

            return jsonify({
                "success": False,
                "message": user_message,
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError", 
                    "details": f"Internal error of type: {error_type}" 
                }
            }), 500

        except Exception as e:
            logger.error(f"Controller: Unexpected error changing task status for task '{task_id}': {e}", exc_info=True)
            return jsonify({
                "success": False,
                "message": "An unexpected error occurred. Please try again later.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "details": "An unexpected error occurred."
                }
            }), 500
        
    def delete_task(self, user_id: str, project_id: str, task_id: str):
        logger.info(f"Controller: Received request to delete task '{task_id}' in project '{project_id}' by user '{user_id}'")
        try:
            # Chama o serviço para deletar
            self.service.delete_task(
                user_id=user_id,
                project_id=project_id,
                task_id=task_id
            )

            return jsonify({
                "success": True,
                "message": "Task deleted successfully.",
                "data": None,
                "error": None
            }), 200

        except (ProjectNotFoundError, TaskNotFoundError) as e:
            error_type = type(e).__name__
            logger.warning(f"Controller: Resource not found during task deletion for task '{task_id}'. {error_type}: {e}")
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {"code": 404, "type": error_type, "details": str(e)}
            }), 404

        except AuthorizationError as e:
            logger.warning(f"Controller: Authorization failed for user '{user_id}' trying to delete task '{task_id}'. {e}")
            return jsonify({
                "success": False,
                "message": "Authorization failed. You do not have permission to delete this task.",
                "data": None,
                "error": {"code": 403, "type": "AuthorizationError", "details": str(e)}
            }), 403

        except DatabaseError as e:
            logger.error(f"Controller: Database error during task deletion for task '{task_id}'. {e}", exc_info=True)
            return jsonify({
                "success": False,
                "message": "An internal server error occurred while deleting the task.",
                "data": None,
                "error": {"code": 500, "type": "InternalServerError", "details": "Database operation failed."}
            }), 500

        except Exception as e:
            logger.error(f"Controller: Unexpected error deleting task '{task_id}': {e}", exc_info=True)
            return jsonify({
                "success": False,
                "message": "An unexpected error occurred. Please try again later.",
                "data": None,
                "error": {"code": 500, "type": "InternalServerError", "details": "An unexpected error occurred."}
            }), 500

        

        
    # def delete_task(self, project_id, task_id):
    #     try:
    #         self.service.delete_task(project_id=project_id, task_id=task_id)
    #         return jsonify({
    #             "success": True,
    #             "message": "To-Do deleted successfully.",
    #             "data": None,
    #             "error": None
    #         }), 200
    #     except TaskNotFoundError as e:
    #         return jsonify({
    #             "success": False,
    #             "message": "To-Do not found.",
    #             "data": None,
    #             "error": {
    #                 "code": 404,
    #                 "type": "TodoNotFoundError",
    #                 "details": str(e)
    #             }
    #         }), 404
    #     except Exception as e:
    #         return jsonify({
    #             "success": False,
    #             "message": "Something went wrong. Please try again later.",
    #             "data": None,
    #             "error": {
    #                 "code": 500,
    #                 "type": "InternalServerError",
    #                 "details": str(e)
    #             }
    #         }), 500 
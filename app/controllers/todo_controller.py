from flask import jsonify, render_template, abort
from app.services.todo_service import ToDoService
from ..models.exceptions import DatabaseError, ToDoValidationError, TodoNotFoundError
from ..utils.logger import logger

class ToDoController:
    def __init__(self):
        try:
            self.service = ToDoService()
        except DatabaseError as e:
            raise DatabaseError(f"Failed to initialize TaskService: {str(e)}")

    def create_to_do(self, data, task_id):
        name = data.get('name')
        try:        
            new_to_do = self.service.create_todo(task_id=task_id, to_do_name=name)
            return jsonify({
                "success": True,
                "message": "To-Do created successfully",
                "data": {
                    "id": new_to_do.identificator,
                    "title": new_to_do.title,
                    "created_time": new_to_do.created_time_formatted,
                    "status": new_to_do.status
                },
                "error": None
            }), 201
        except ToDoValidationError as e:
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {
                    "code": 400,
                    "type": "ToDoValitantionError",
                    "details": str(e)
                }
            }), 400
        except Exception as e:
            logger.error(f"Erro ao criar to-do para a task {task_id}: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Something went wrong. Please try again later.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "details": str(e)
                }
            }), 500


    def change_to_do_state(self, data, todo_id, task_id):
        try:
            new_status = data.get('status')
            updated_to_do = self.service.change_to_do_state(todo_id=todo_id, new_status=new_status, task_id=task_id)
            return jsonify({
                "success": True,
                "message": "To-Do status changed successfully",
                "data": {
                    "status": updated_to_do.status,
                    "created_time": updated_to_do.created_time_formatted,
                    "completed_time": getattr(updated_to_do, "completed_time_formatted", None)
                },
                "error": None
            }), 200
        
        # Isso aqui não é 404, não é not found pq apareceu na tela pro usuario, é erro de servidor, algo de errado no codigo, tem que ser 500.
        except TodoNotFoundError as e:
           return jsonify({
                "success": False,
                "message": "To-Do not found.",
                "data": None,
                "error": {
                    "code": 404,
                    "type": "TodoNotFoundError",
                    "details": str(e)
                }
            }), 404
        except ToDoValidationError as e:
            logger.error(f"Erro ao atualizar o status To-Do {todo_id}")
            return jsonify({
                "success": False,
                "message": "An error occurred while processing your request. Please check the information provided and try again.",
                "data": None,
                "error": {
                    "code": 400,
                    "type": "ToDoValitantionError",
                    "details": str(e)
                }
            }), 400
        except Exception as e:
            logger.error(f"Erro ao atualizar o status do to-do {todo_id}: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Something went wrong. Please try again later.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "details": str(e)
                }
            }), 500
        

    def delete_to_do(self, todo_id, task_id):
        try:
            self.service.delete_to_do(to_do_id=todo_id, task_id=task_id)
            return jsonify({
                "success": True,
                "message": "To-Do deleted successfully.",
                "data": None,
                "error": None
            }), 200
        except TodoNotFoundError as e:
            return jsonify({
                "success": False,
                "message": "To-Do not found.",
                "data": None,
                "error": {
                    "code": 404,
                    "type": "TodoNotFoundError",
                    "details": str(e)
                }
            }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Something went wrong. Please try again later.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "details": str(e)
                }
            }), 500
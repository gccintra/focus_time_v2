from flask import jsonify, render_template, abort
from app.services.task_service import TaskService
from app.services.task_todo_service import TaskToDoService
from ..models.exceptions import DatabaseError, TaskNotFoundError, TaskValidationError
from ..utils.logger import logger

class TaskController:
    def __init__(self):
        try:
            self.service = TaskService()
            self.task_todo_service = TaskToDoService()
        except DatabaseError as e:
            raise DatabaseError(f"Failed to initialize TaskService: {str(e)}")

    def my_tasks(self, user=None):
        tasks = self.service.get_all_tasks(user_id=user.identificator)
        return render_template("my_tasks.html", title="My Tasks", tasks=tasks, active_page='home', user=user)

    def get_data_for_all_charts(self, user_id):
        tasks_for_chart = self.service.get_data_for_all_charts(user_id=user_id)
        return jsonify({
            "success": True,
            "message": "Data rescued successfully",
            "data": {
                "tasks": tasks_for_chart
            }, 
            "error": None
            }), 200

    def new_task(self, data, user_id):
        task_name = data.get('name') if isinstance(data, dict) else None
        task_color = data.get('color') if isinstance(data, dict) else None
        try:
            task = self.service.create_new_task(name=task_name, color=task_color, user_id=user_id)
            return jsonify({
                "success": True,
                "message": "Task created successfully",
                "data": {
                    'id': task.identificator,
                    'name': task.title,
                    'color': task.color,
                    'today_total_time': task.today_total_time,
                    'week_total_time': task.week_total_time
                },
                "error": None
            }), 200
        except TaskValidationError as e:
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {
                    "code": 400,
                    "type": "BadRequest",
                    "details": str(e)
                }
            }), 400
        except Exception as e:   #TypeError, Exception
            logger.error(f"Erro ao criar a task {task_name}: {str(e)}")
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

    def start_task(self, task_id, user=None):
        try:
            task, todo_list = self.task_todo_service.get_task_todo_list(task_id=task_id, user_id=user.identificator)
            return render_template("start_task.html", title="Start Task", task=task, to_do_list=todo_list, user=user)
        except TaskNotFoundError:
            return abort(404)
        except Exception as e:   
            logger.error(f"Erro ao acessar a task {task_id}: {str(e)}")
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

    def update_task_time(self, task_id, user_id, data):
        elapsed_seconds = int(data.get("elapsed_seconds")) if isinstance(data, dict) else None

        try:
            self.service.update_task_time(task_id=task_id, elapsed_seconds=elapsed_seconds, user_id=user_id,)
            return jsonify({
                "success": True,
                "message": "The seconds have been saved.",
                "data": None,
                "error": None
            }), 200
        except TaskNotFoundError as e:
            return jsonify({
                "success": False,
                "message": "Task not found.",
                "data": None,
                "error": {
                    "code": 404,
                    "type": "TaskNotFoundError",
                    "details": str(e)
                }
            }), 404
        except TaskValidationError as e:
            logger.error(f"Erro ao atualizar o tempo de foco diário para a task {task_id}")
            return jsonify({
                "success": False,
                "message": "An error occurred while processing your request. Please check the information provided and try again.",
                "data": None,
                "error": {
                    "code": 400,
                    "type": "TaskValidationError",
                    "details": str(e)
                }
            }), 400
        except Exception as e:   
            logger.error(f"Erro ao atualizar o tempo de foco diário para a task {task_id}: {str(e)}")
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
          

    def get_data_for_last_365_days_home_chart(self, user_id=None):
        minutes_per_day = self.service.get_data_for_last_365_days_home_chart(user_id=user_id)
        return jsonify({
                "success": True,
                "message": 'data rescued successfully',
                "data":  {
                    "minutes_per_day": minutes_per_day
                },
                "error": None
            }), 200


    
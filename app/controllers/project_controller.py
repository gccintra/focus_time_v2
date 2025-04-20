from flask import jsonify, render_template, abort
from app.services.project_service import ProjectService
from ..models.exceptions import DatabaseError, ProjectNotFoundError, ProjectValidationError
from ..utils.logger import logger

class ProjectController:
    def __init__(self):
        self.service = ProjectService()

    def my_projects(self, user=None):
        try:
            projects = self.service.get_projects_with_time_summary(user_id=user.identificator)
            return render_template("my_projects.html", title="My Projects", projects=projects, active_page='home', user=user)
        except Exception as e:
            logger.error(f"Erro ao buscar os projects de {user.username}: {str(e)}")
            return abort(500)
    
    def create_new_project(self, data, user_id):
        project_title = data.get('title') if isinstance(data, dict) else None
        project_color = data.get('color') if isinstance(data, dict) else None
        try:
            project = self.service.create_new_project(title=project_title, color=project_color, user_id=user_id)
            return jsonify({
                "success": True,
                "message": "Project created successfully",
                "data": {
                    'identificator': project.identificator,
                    'title': project.title,
                    'color': project.color,
                    'today_total_time': '00h00m', 
                    'week_total_time': '00h00m',
                    'today_total_minutes': 0,
                    'week_total_minutes': 0
                },
                "error": None
            }), 200
        except ProjectValidationError as e:
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
            logger.error(f"Erro ao criar a project {project_title}: {str(e)}")
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




    def project_room(self, project_id, user):
        try:
            project = self.service.get_details_for_project_room(project_id=project_id, user_id=user.identificator)
            return render_template("project_room.html", title=project["project"]["title"], project=project, user=user)
        except ProjectNotFoundError:
            return abort(404)
        except Exception as e:   
            logger.error(f"Erro ao acessar a task {project_id}: {str(e)}")
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
        except ProjectNotFoundError as e:
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
        except ProjectNotFoundError as e:
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


    
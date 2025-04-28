from flask import Blueprint, request
from app.controllers.task_controller import TaskController
from ..utils.auth_decorator import login_required 


task_bp = Blueprint("task", __name__, url_prefix="/task")
task_controller = TaskController()

@task_bp.route("/<project_id>/create_task", methods=["POST"])
@login_required  
def create_task_route(project_id):
    user_id = request.current_user.identificator
    data = request.get_json()
    return task_controller.create_task(user_id=user_id, project_id=project_id, data=data)

@task_bp.route("/<project_id>/change_status/<task_id>", methods=["PUT"])
@login_required  
def change_task_status_route(project_id, task_id):
    data = request.get_json()
    user_id = request.current_user.identificator
    return task_controller.change_task_status(user_id=user_id, project_id=project_id, task_id=task_id, data=data)

@task_bp.route("/<project_id>/delete/<task_id>", methods=["DELETE"])
@login_required   
def delete_task_route(project_id, task_id):
    user_id = request.current_user.identificator
    return task_controller.delete_task(user_id=user_id, project_id=project_id, task_id=task_id)

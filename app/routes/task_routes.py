from flask import Blueprint, request
from app.controllers.task_controller import TaskController
from ..utils.auth_decorator import login_required 


task_bp = Blueprint("taskk", __name__, url_prefix="/task")
task_controller = TaskController()

@task_bp.route("/<task_id>/create_task", methods=["POST"])
@login_required  
def new_todo_route(task_id):
    data = request.get_json()
    return task_controller.create_to_do(data=data, task_id=task_id)

@task_bp.route("/<project_id>/change_state/<task_id>", methods=["PUT"])
@login_required  
def change_to_do_state_route(project_id, task_id):
    data = request.get_json()
    return task_controller.change_to_do_state(data=data, todo_id=task_id, task_id=project_id)

@task_bp.route("/<project_id>/delete/<task_id>", methods=["DELETE"])
@login_required   
def delete_todo_route(project_id, task_id):
    return task_controller.delete_to_do(todo_id=task_id, task_id=project_id)

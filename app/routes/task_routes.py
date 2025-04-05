from flask import Blueprint, request, redirect, url_for
from app.controllers.task_controller import TaskController
from ..utils.auth_decorator import login_required


task_bp = Blueprint("task", __name__, url_prefix="/task")
task_controller = TaskController()

@task_bp.route("/", methods=["GET"])
@login_required  
def tasks_route():
    user = request.current_user
    return task_controller.my_tasks(user=user)

@task_bp.route("/get_data_for_all_doughnut_home_charts", methods=["GET"])
@login_required 
def get_data_for_all_charts_menu_route():
    user_id = request.current_user.identificator
    return task_controller.get_data_for_all_charts(user_id=user_id)

@task_bp.route("/new_task", methods=["POST"])
@login_required 
def new_task_route():
    user_id = request.current_user.identificator
    data = request.get_json()
    return task_controller.new_task(data=data, user_id=user_id)

@task_bp.route("/<task_id>", methods=["GET"])
@login_required   
def start_task_route(task_id):
    user = request.current_user
    return task_controller.start_task(task_id=task_id, user=user)

@task_bp.route("/update_task_time/<task_id>", methods=["POST", "PUT"])
@login_required 
def update_task_time_route(task_id):
    user_id = request.current_user.identificator
    data = request.get_json()
    return task_controller.update_task_time(task_id=task_id, user_id=user_id, data=data)

@task_bp.route("/get_data_for_last_365_days_home_chart", methods=["GET"])
@login_required 
def get_data_for_last_365_days_home_chart_route():
    user_id = request.current_user.identificator
    return task_controller.get_data_for_last_365_days_home_chart(user_id=user_id)




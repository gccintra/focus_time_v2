from flask import Blueprint, request, redirect, url_for
from app.controllers.project_controller import ProjectController
from ..utils.auth_decorator import login_required


project_bp = Blueprint("project", __name__, url_prefix="/project")
project_controller = ProjectController()

@project_bp.route("/", methods=["GET"])
@login_required  
def projects_route():
    user = request.current_user
    return project_controller.my_projects(user=user)

@project_bp.route("/create_project", methods=["POST"])
@login_required 
def create_project_route():
    user_id = request.current_user.identificator
    data = request.get_json()
    return project_controller.create_new_project(data=data, user_id=user_id)

@project_bp.route("/get_data_for_last_365_days_home_chart", methods=["GET"])
@login_required 
def get_data_for_last_365_days_home_chart_route():
    user_id = request.current_user.identificator
    return project_controller.get_data_for_last_365_days_home_chart(user_id=user_id)

@project_bp.route("/<project_id>", methods=["GET"])
@login_required   
def project_room_route(project_id):
    user = request.current_user
    return project_controller.project_room(project_id=project_id, user=user)




@project_bp.route("/update_task_time/<task_id>", methods=["POST", "PUT"])
@login_required 
def update_project_time_route(task_id):
    user_id = request.current_user.identificator
    data = request.get_json()
    return project_controller.update_task_time(task_id=task_id, user_id=user_id, data=data)


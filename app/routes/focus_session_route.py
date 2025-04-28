from flask import Blueprint, request, redirect, url_for
from app.controllers.focus_session_controller import FocusSessionController
from ..utils.auth_decorator import login_required


focus_session_bp = Blueprint("focus_session", __name__, url_prefix="/focus_session")
focus_session_controller = FocusSessionController()

# Alterar a rota, colocar o id do project aqui, inves de colocar no corpo da requisição, para seguir um padrao
@focus_session_bp.route("/save", methods=["POST"])
@login_required  
def focus_session_save_route():
    user_id = request.current_user.identificator
    data = request.get_json()
    return focus_session_controller.save_focus_session(user_id=user_id, data=data)


# @project_bp.route("/create_project", methods=["POST"])
# @login_required 
# def create_project_route():
#     user_id = request.current_user.identificator
#     data = request.get_json()
#     return project_controller.create_new_project(data=data, user_id=user_id)


# project_bp = Blueprint("project", __name__, url_prefix="/project")
# project_controller = ProjectController()
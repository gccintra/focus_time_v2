from flask import Blueprint, request
from app.controllers.todo_controller import ToDoController
from ..utils.auth_decorator import login_required 


todo_bp = Blueprint("todo", __name__, url_prefix="/todo")
todo_controller = ToDoController()

@todo_bp.route("/<task_id>/new_todo", methods=["POST"])
@login_required  
def new_todo_route(task_id):
    """Cria um novo ToDo para uma tarefa específica."""
    data = request.get_json()
    return todo_controller.create_to_do(data=data, task_id=task_id)

@todo_bp.route("/change_state/<task_id>/<todo_id>", methods=["PUT"])
@login_required  
def change_to_do_state_route(task_id, todo_id):
    """Altera o estado de um ToDo específico."""
    data = request.get_json()
    return todo_controller.change_to_do_state(data=data, todo_id=todo_id, task_id=task_id)

@todo_bp.route("/delete/<task_id>/<todo_id>", methods=["DELETE"])
@login_required   
def delete_todo_route(task_id, todo_id):
    """Deleta um ToDo específico."""
    return todo_controller.delete_to_do(todo_id=todo_id, task_id=task_id)

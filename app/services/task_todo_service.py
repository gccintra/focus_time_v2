from app.services.task_service import TaskService
from app.services.todo_service import ToDoService
from app.models.exceptions import TaskNotFoundError

class TaskToDoService():
    def __init__(self):
        self.task_service = TaskService()
        self.todo_service = ToDoService()

    def get_task_todo_list(self, task_id, user_id=None):
        try:
            task = self.task_service.get_task_by_id(task_id=task_id, user_id=user_id)
            todo_list = self.todo_service.get_todo_list(task_id=task_id)
            return task, todo_list
        except (TaskNotFoundError, Exception):
            raise
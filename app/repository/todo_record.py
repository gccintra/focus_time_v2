from .data_record import DataRecord
from ..models.task import Task
from ..models.exceptions import TaskNotFoundError, TodoNotFoundError
import uuid, json
from ..utils.logger import logger

class ToDoRecord(DataRecord):
    def __init__(self):
        super().__init__("todo.json")
  
    def id_exists(self, todo_list, new_id):
        return any(todo.identificator == new_id for todo in todo_list)
    
    def generate_unique_id(self):
        todo_full_list = self.get_models()
        new_id = f'todo-{uuid.uuid4()}'
        while self.id_exists(todo_full_list, new_id):
            new_id = f'todo-{uuid.uuid4()}' 
        return new_id
    
    def get_todo_by_id(self, todo_id, task_id=None):
        todo_full_list = self.get_models(task_id=task_id)
        try:
            for record in todo_full_list:
                if record.identificator == todo_id:
                    logger.info(f'To Do com id {todo_id} encontrada com sucesso!')
                    return record
            logger.warning(f"To Do com id '{todo_id}' não foi encontrado.")
            raise TodoNotFoundError(task_id=todo_id)
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar to-do por ID '{todo_id}': {e}")
            raise

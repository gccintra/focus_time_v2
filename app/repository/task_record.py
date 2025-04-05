from .data_record import DataRecord
from ..models.task import Task
from ..models.exceptions import TaskNotFoundError
import uuid
import json
from ..utils.logger import logger

class TaskRecord(DataRecord):
    def __init__(self):
        super().__init__("task.json")

    def id_exists(self, task_list, new_id):
        return any(task.identificator == new_id for task in task_list)

    def generate_unique_id(self):
        task_full_list = self.get_models()
        new_id = f'task-{uuid.uuid4()}'
        while self.id_exists(task_full_list, new_id):
            new_id = f'task-{uuid.uuid4()}'
        return new_id
    
    def get_task_by_id(self, task_id, user_id=None):
        task_full_list = self.get_models(user_id=user_id)
        try:
            for record in task_full_list:
                if record.identificator == task_id:
                    logger.info(f'Task com id {task_id} encontrada com sucesso!')
                    return record
            logger.warning(f"Task com id '{task_id}' não foi encontrado.")
            raise TaskNotFoundError(task_id=task_id)
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar task por ID '{task_id}': {e}")
            raise
    
   
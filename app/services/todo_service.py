from ..models.todo import ToDo
from ..models.exceptions import ToDoValidationError, TodoNotFoundError
from ..repository.todo_record import ToDoRecord
from datetime import datetime
from ..utils.logger import logger
from ..models.exceptions import DatabaseError

class ToDoService:
    def __init__(self):
        try:
            self.db = ToDoRecord()
        except ValueError as e:
            logger.error(f"Erro ao inicializar ToDoRecord: {e}")
            raise DatabaseError("Erro ao inicializar o banco de dados.")

    def create_todo(self, task_id, to_do_name):
        try:
            identificator = self.db.generate_unique_id()
            new_to_do = ToDo(title=to_do_name, identificator=identificator, task_FK=task_id)
            self.db.write(new_to_do)
            logger.info(f'To do {to_do_name} para a task {task_id} criado com sucesso!')
            return new_to_do
        except ToDoValidationError as e:
            logger.warning(f"To-do creation failed: {str(e)}")
            raise
        except (TypeError, Exception):
            raise

    def get_todo_list(self, task_id):
        try:
            todo_list = self.db.get_models(task_id=task_id)
            print(f"get_to_do_list: {task_id}")

            logger.info(f'Retornando a lista de todo para a task {task_id} com sucesso!')
            return todo_list
        except Exception as e:
            logger.error(e)

    def change_to_do_state(self, todo_id, new_status, task_id):
        try:
            todo = self.get_todo_by_id(todo_id=todo_id, task_id=task_id)

            if new_status == 'completed':
                todo.mark_as_completed()
            elif new_status == 'in progress':
                todo.mark_as_in_progress()
            else:
                todo.status = 'invalid status'

            self.db.save()      
            logger.info(f'Status do To Do com id {todo_id} atualizado para {new_status} com sucesso!')
            return todo
        except ToDoValidationError as e:
            logger.error(e)
            raise
        except TodoNotFoundError as e:
            logger.warning(f'Erro ao atualizar o status to-do: {e}')
            raise         
        except Exception as e:
            logger.error(f'Erro ao atualizar o status to-do: {e}')
            raise

    def delete_to_do(self, to_do_id, task_id=None):
        try:
            todo_list = self.db.get_models(task_id=task_id)

            for todo in todo_list: 
                if todo.identificator == to_do_id:
                    todo.mark_as_deleted()
                    self.db.save()  
                    logger.info(f'To-do {todo.title} ({todo.identificator}) removido com sucesso!')
                    return
            raise TodoNotFoundError(to_do_id)
        except TodoNotFoundError as e:
            logger.warning(f'Erro ao deletar o to-do {to_do_id}: {e}')
            raise         
        except Exception as e:
            logger.error(f'Erro ao deletar o to-do {to_do_id}: {e}')
            raise

    def get_todo_by_id(self, todo_id, task_id=None):
        try:
            return self.db.get_todo_by_id(todo_id, task_id)
        except (TodoNotFoundError, Exception):
            raise

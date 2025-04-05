import json
import os
import shutil
from ..models.task import Task
from ..models.todo import ToDo
from ..models.user import User
from ..utils.logger import logger

class DataRecord:
    def __init__(self, filename):
        self.models_classes = {
            'user.json': User,
            'task.json': Task,
            'todo.json': ToDo,
            'test_task.json': Task   
        }

        self._filename = "app/repository/database/" +  filename
        self.model_class = self.models_classes.get(filename)

        if not self.model_class:
            logger.error(f"Arquivo '{filename}' não possui classe associada!")
            raise ValueError(f"Arquivo '{filename}' não possui classe associada!")

        self._models = []

        if self.model_class == User:
            self.read()

    def read(self, user_id=None, task_id=None):
        print(f"Lendo arquivo {self._filename} - user_id: {user_id}, task_id: {task_id}")
        try:
            with open(self._filename, "r", encoding="utf-8") as fjson:

                file_data = json.load(fjson)

                if self.model_class == User:
                    self._models = [self.model_class(**data, hashed=True) for data in file_data] 
                    return
                
                if user_id:
                    self._models = [self.model_class(**data) for data in file_data if data.get('user_FK') == user_id]
                elif task_id:
                    self._models = [self.model_class(**data) for data in file_data if data.get('task_FK') == task_id]
                else:
                    self._models = [self.model_class(**data) for data in file_data]

        except FileNotFoundError:
            logger.warning(f"Arquivo '{self._filename}' não encontrado! Iniciando com lista vazia.")
            self._models = []
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON do arquivo '{self._filename}': {e}\n Iniciando com lista vazia.")
            self._models = []
        except Exception as e:
            logger.error(f"Erro inesperado ao ler o arquivo '{self._filename}': {e} \n Iniciando com lista vazia.")
            self._models = []

    def write(self, model):
        try:
            if not isinstance(model, self.model_class):
                raise TypeError(f"Esperado instância de '{self.model_class.__name__}', mas recebido '{type(model).__name__}'.")

            self._models.append(model)
            self.save()
            logger.info(f"Novo registro adicionado e salvo: {model}.")
        except TypeError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Erro ao adicionar novo registro ao banco de dados: {e}")
            raise

    def save(self):
        temp_filename = self._filename + ".tmp"
        backup_filename = self._filename + ".bak"

        if os.path.exists(temp_filename):
            logger.warning(f"Arquivo temporário encontrado: {temp_filename}. Excluindo...")
            os.remove(temp_filename)

        try:
            # Ler todos os registros existentes
            try:
                with open(self._filename, "r", encoding="utf-8") as fjson:
                    existing_data = json.load(fjson)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []

            # Criar um dicionário {identificador:  } para facilitar atualizações
            existing_dict = {item["identificator"]: item for item in existing_data}


            # Atualizar ou adicionar os modelos novos/modificados
            for model in self._models:
                existing_dict[model.identificator] = model.to_dict()


            # Filtra os itens que não estão marcados como 'deleted' e cria a lista final_data
            final_data = [item for item in existing_dict.values() if item.get("status") != "deleted"]

            # Remove os modelos marcados como 'deleted' de self._models
            self._models = [model for model in self._models if hasattr(model, 'status') and model.status != 'deleted']

            # Criar um backup antes de modificar o arquivo original
            if os.path.exists(self._filename):
                shutil.copy(self._filename, backup_filename)

            # Salvar os dados no arquivo temporário primeiro
            with open(temp_filename, "w", encoding="utf-8") as fjson:
                json.dump(final_data, fjson, indent=4, ensure_ascii=False)

            # Testar a integridade do JSON antes de substituir o original
            with open(temp_filename, "r", encoding="utf-8") as fjson:
                json.load(fjson)  # Testa se o JSON está válido

            # Substituir o arquivo original pelo novo apenas se tudo estiver certo
            os.replace(temp_filename, self._filename)

            logger.info(f"{len(self._models)} registros salvos em '{self._filename}'.")

        except Exception as e:
            logger.error(f"Erro ao salvar os dados no banco de dados: {e}")

            # Restaurar backup em caso de erro
            if os.path.exists(backup_filename):
                shutil.copy(backup_filename, self._filename)
                logger.warning(f"Backup restaurado para '{self._filename}'.")

            raise
        finally:
            if os.path.exists(temp_filename):  # Garante que o temp seja removido se falhar
                os.remove(temp_filename)


    def get_models(self, user_id=None, task_id=None):
        if user_id:
            self.read(user_id=user_id)
        elif task_id:
            self.read(task_id=task_id)
        else:
            self.read()

        return self._models
 
    


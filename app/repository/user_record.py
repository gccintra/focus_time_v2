from .data_record import DataRecord
from ..utils.logger import logger
from app.models.user import User
import json
import uuid
from ..models.exceptions import UserNotFoundError, UsernameAlreadyExists, EmailAlreadyExists



class UserRecord(DataRecord):
    def __init__(self):
        super().__init__('user.json')
        

    def id_exists(self, users_full_list, new_id):
        return any(user.identificator == new_id for user in users_full_list)

    def generate_unique_id(self):
        users_full_list = self.get_models()
        new_id = f'user-{uuid.uuid4()}'
        while self.id_exists(users_full_list, new_id):
            new_id = f'user-{uuid.uuid4()}'
        return new_id
    

    # Depois criar um get_user_by_any_data e usar getattr pro user.email por exemplo, da pra usar so uma funcao pra buscar o usuario por qualquer dado, só colocar o dado que eu quero como um parametro
    def get_user_by_email(self, email):
        users_list = self.get_models()
        for user in users_list:
            if user.email == email:
                logger.info(f'User com email "{email}" encontrada com sucesso!')
                return user
        logger.warning(f"User com e-mail '{email}' não foi encontrado.")
        raise UserNotFoundError(user_identificator=email)
    

    def get_user_by_id(self, user_id):
        users_list = self.get_models()
        for user in users_list:
            if user.identificator == user_id:
                logger.info(f'User com id "{user_id}" encontrada com sucesso!')
                return user
        logger.warning(f"User com id '{user_id}' não foi encontrado.")
        raise UserNotFoundError(user_identificator=user_id)
    

    def verify_unique_email(self, email):
        users_list = self.get_models()
        for user in users_list:
            if user.email == email:
                raise EmailAlreadyExists()
        logger.info(f"Não existe uma conta com o email: '{email}', uma nova conta pode ser criada com esse email.")
        
    def verify_unique_username(self, username):
        users_list = self.get_models()
        for user in users_list:
            if user.username == username:
                raise UsernameAlreadyExists()
        logger.info(f"Não existe uma conta com o username: '{username}', uma nova conta pode ser criada com esse username.")
    
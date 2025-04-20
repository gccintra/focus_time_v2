from ..models.user import User
from ..utils.logger import logger
from ..models.exceptions import UserNotFoundError, InvalidPasswordError, EmailAlreadyExists, UsernameAlreadyExists, InvalidCreatePasswordError, UserValidationError
import datetime
import jwt
from flask import current_app, make_response
from app.infra.repository.user_repository import UserRepository

class AuthService:
    def __init__(self):
        self.repo = UserRepository()

    def create_user(self, user_email, username, password):
        
        try:
            if self.repo.get_by_email(user_email): raise EmailAlreadyExists
            if self.repo.get_by_username(username): raise UsernameAlreadyExists

            user = User(username=username, email=user_email, password=password)
            self.repo.add(user)
            self.repo._session.commit()
            logger.info(f'User {username} criado com sucesso!')
            return user

        except (UsernameAlreadyExists, EmailAlreadyExists) as e:
            logger.warning(f"Falha ao criar usuário: {e}")  # Agora funciona para ambos os casos
            self.repo._session.rollback()
            raise
        except InvalidCreatePasswordError as e:
            logger.warning(f"Falha ao criar usuário: {e}")
            self.repo._session.rollback()
            raise
        except UserValidationError as e:
            logger.warning(f"Falha ao criar usuário: {e}")
            self.repo._session.rollback()
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar usuário: {e}")
            self.repo._session.rollback()
            raise

    def login(self, user_email, password):
        try:
            user = self.repo.get_by_email(user_email)

            if not user:
                logger.error(f"Usuário com email '{user_email}' não tem cadastro no sistema.")
                raise UserNotFoundError

            if not user.verify_password(password):
                logger.error(f"Senha incorreta para o usuário com email '{user_email}'.")
                raise InvalidPasswordError()
            
            token = self.create_jwt_token(user)
            logger.info(f"Login bem-sucedido para o usuário: {user.username} ({user_email})")

            return token

        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao fazer login para o usuário '{user_email}': {e}")
            self.repo._session.rollback()
            raise

                    
    def create_jwt_token(self, user):
        secret_key = current_app.config["SECRET_KEY"]
        
        payload = {
            'id': user.identificator,  
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6)  
        }

        # Gere o JWT usando a chave secreta e o payload
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return token
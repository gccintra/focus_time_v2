from ..repository.user_record import UserRecord
from ..models.user import User
from ..utils.logger import logger
from ..models.exceptions import UserNotFoundError, InvalidPasswordError, EmailAlreadyExists, UsernameAlreadyExists, InvalidCreatePasswordError, UserValidationError
import datetime
import jwt
from flask import current_app, make_response
from ..utils.utils import validate_password

class AuthService:
    def __init__(self):
        self.db = UserRecord()

    def create_user(self, user_email, username, password):
        identificator = self.db.generate_unique_id()
        
        try:
            self.db.verify_unique_email(user_email)
            self.db.verify_unique_username(username)

            user = User(identificator=identificator, username=username, email=user_email, password=password)
            self.db.write(user)

            logger.info(f'User {username} criado com sucesso!')
            return user

        except (UsernameAlreadyExists, EmailAlreadyExists) as e:
            logger.warning(f"Falha ao criar usuário: {e}")  # Agora funciona para ambos os casos
            raise
        except InvalidCreatePasswordError as e:
            logger.warning(f"Falha ao criar usuário: {e}")
            raise
        except UserValidationError as e:
            logger.warning(f"Falha ao criar usuário: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar usuário: {e}")
            raise

    def login(self, user_email, password):
        try:
            user = self.db.get_user_by_email(user_email)

            if not user.verify_password(password):
                logger.error(f"Senha incorreta para o usuário com email '{user_email}'.")
                raise InvalidPasswordError()
            
            token = self.create_jwt_token(user)

            return token

        except UserNotFoundError:
            logger.error(f"Usuário com email '{user_email} não tem cadastro no sistema.")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao fazer login para o usuário '{user_email}': {e}")
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
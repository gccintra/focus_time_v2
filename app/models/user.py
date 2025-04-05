import bcrypt
from app.models.exceptions import UserValidationError, InvalidCreatePasswordError
import re

class User:
    def __init__(self, identificator, username, email, password, status=None, hashed=False):
        self.__identificator = identificator

        self._username = None
        self.username = username

        self._email = None
        self.email = email

        self._password = None
        if hashed:
           self._password = password
        else:
            self.password = password 
            
        self._status = None
        self.status = status or 'active'

    @property
    def identificator(self):
        return self.__identificator

    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, value):
        if not value:
            raise UserValidationError("Username", "Username cannot be empty.")
        self._username = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not value:
            raise UserValidationError("Email", "Email cannot be empty.")
        if "@" not in value:
            raise UserValidationError("Email", "Invalid email format.")
       
        self._email = value
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        valid_statuses = ["active"]
        if value not in valid_statuses:
            raise UserValidationError("Status", f"Invalid status. Choose one: {', '.join(valid_statuses)}.")
        self._status = value

    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, value):
        if len(value) < 6:
            raise InvalidCreatePasswordError("Password must be at least 6 characters long.")

        if not re.search(r"[A-Za-z]", value):
            raise InvalidCreatePasswordError("The password must contain at least one letter.")

        if not re.search(r"\d", value):
            raise InvalidCreatePasswordError("The password must contain at least one number.")

        self._password = self.__generate_password_hash(value)


    def __generate_password_hash(self, password):
        """Gera um hash seguro para a senha"""

        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password):
        """Verifica se a senha digitada corresponde ao hash salvo"""
        return bcrypt.checkpw(password.encode('utf-8'), self._password.encode('utf-8'))

    def to_dict(self):
        """Retorna um dicionário representando o usuário"""
        return {
            "identificator": self.__identificator,
            "username": self.username,
            "email": self.email,
            "password": self._password,
            "status": self._status
        } 
    



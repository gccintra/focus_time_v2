import bcrypt, re, uuid
from app.models.exceptions import UserValidationError, InvalidCreatePasswordError
from app.infra.entities.user_db import UserDB


class User:
    def __init__(self, username, email, password, active=True, hashed=False, identificator=None):
        self.identificator = identificator if identificator is not None else str(uuid.uuid4())
        self.username = username
        self.email = email

        if hashed:
           self._password = password
        else:
            self.password = password 
            
        self.active = active

    @property
    def identificator(self):
        return self._identificator
    
    @identificator.setter
    def identificator(self, value):
        if not value:
            raise UserValidationError("User Identificator", "User Identificator cannot be empty.")
        self._identificator = value


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
    def active(self):
        return self._active
    
    @active.setter
    def active(self, value):
        if not isinstance(value, bool):
            raise UserValidationError("Active", "Invalid value. 'active' must be a boolean.")
        self._active = value

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
    

    @classmethod
    def from_orm(cls, user_db: 'UserDB') -> 'User':
        if not user_db:
            return None # Retorna None se a entidade do DB for None

        return cls(
            identificator=user_db.identificator,
            username=user_db.username,
            email=user_db.email,
            password=user_db.password, 
            active=user_db.active,
            hashed=True
        )

    def to_orm(self) -> 'UserDB':
        return UserDB(
            identificator=self._identificator,
            username=self._username,
            email=self._email,
            password=self._password,
            active=self._active
        )


    def __repr__(self):
        return f"<User(identificator='{self.identificator}', username='{self.username}', email='{self.email}')>"





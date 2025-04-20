class ProjectError(Exception):
    """Erro geral relacionado a tarefas."""
    def __init__(self, message="Erro relacionado ao projeto."):
        super().__init__(message)


class ProjectNotFoundError(ProjectError):
    """Erro para quando um project não é encontrada."""
    def __init__(self, project_id=None, message="Project Not Found."):
        if project_id:
            message = f"Project ID '{project_id}' not found."
        super().__init__(message)

class ProjectValidationError(ProjectError):
    def __init__(self, field=None, message=None):
        if field and not message:
            message = f"The field '{field}' is required or contains invalid data."
        elif field and message:
            message = f"Validation error in field '{field}': {message}"
        elif not message and not field:
            message = "Project validation failed due to invalid or missing data."
        super().__init__(message)


class DatabaseError(Exception):
    """Erro geral relacionado ao banco de dados."""
    def __init__(self, message="Erro ao acessar o banco de dados."):
        super().__init__(message)


class TaskError(Exception):
    """Erro geral relacionado ao ToDo."""
    def __init__(self, message="Erro relacionado ao Tas."):
        super().__init__(message)


class TaskNotFoundError(TaskError):
    """Erro para quando uma task não é encontrada."""
    def __init__(self, todo_id=None, message="To-do não encontrado."):
        if todo_id:
            message = f"To-do com ID '{todo_id}' não foi encontrado."
        super().__init__(message)


class TaskValidationError(TaskError):
    """Erro para validação de dados."""
    def __init__(self, field=None, message=None):
        if field and not message:
            message = f"The field '{field}' is required or contains invalid data."
        elif field and message:
            message = f"Validation error in field '{field}': {message}"
        elif not message and not field:
             message = f"Task validation failed due to invalid or missing data."
        super().__init__(message)





class UserError(Exception):
    """Erro geral relacionado ao ToDo."""
    def __init__(self, message="Erro relacionado ao User."):
        super().__init__(message)


class UserNotFoundError(UserError):
    """Erro para quando um user não é encontrada."""
    def __init__(self, user_identificator=None, message="User não encontrado."):
        if user_identificator:
            message = f"User com identificação '{user_identificator}' não foi encontrado."
        super().__init__(message)


class InvalidPasswordError(UserError):
    """Erro para quando a senha é incorreta para autenticação."""
    def __init__(self, message="Invalid Password!"):
        super().__init__(message)


class EmailAlreadyExists(UserError):
    def __init__(self, message="Already have an account with this email, try another!"):
        super().__init__(message)


class UsernameAlreadyExists(UserError):
    def __init__(self, message="Already have an account with this username, try another!"):
        super().__init__(message)


class UserValidationError(UserError):
    """Erro para validação de dados."""
    def __init__(self, field=None, message=None):
        if field and not message:
            message = f"The field '{field}' is required or contains invalid data."
        elif field and message:
            message = f"Validation error in field '{field}': {message}"
        elif not message and not field:
             message = f"User validation failed due to invalid or missing data."
        super().__init__(message)

class InvalidCreatePasswordError(UserError):
    """Erro para quando a senha é incorreta para autenticação."""
    def __init__(self, message="Invalid Password Format!"):
        super().__init__(message)


class TasKStatusError(Exception):
    """Erro geral relacionado ao Status de Task."""
    def __init__(self, message="Erro relacionado ao Task Status."):
        super().__init__(message)


class TaskStatusValidationError(Exception):
    """Erro para validação de dados."""
    def __init__(self, field=None, message=None):
        if field and not message:
            message = f"The field '{field}' is required or contains invalid data."
        elif field and message:
            message = f"Validation error in field '{field}': {message}"
        elif not message and not field:
             message = f"Task Status validation failed due to invalid or missing data."
        super().__init__(message)



class FocusSessionValidationError(Exception):
    """Custom exception for FocusSession validation errors."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation Error on field '{field}': {message}")

# Repositório: Manipula a sessão para carregar, adicionar, atualizar, deletar entidades (session.add, session.query, session.delete, talvez session.flush se precisar de validação antecipada). Não chama commit ou rollback.

# Serviço: Orquestra a lógica de negócio, chama um ou mais métodos de repositório. Define o início e o fim da unidade de trabalho. Chama db.session.commit() dentro de um bloco try...except para finalizar a transação. Chama db.session.rollback() no bloco except se o commit (ou qualquer etapa anterior) falhar.


# Usar flush aqui na repository e commit/rollback na service.


from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select 

from app.models.user import User
from app.infra.entities.user_db import UserDB
from app.infra.db import db 
from app.models.exceptions import UserNotFoundError, UsernameAlreadyExists, EmailAlreadyExists, DatabaseError
from app.utils.logger import logger

class UserRepository:
    def __init__(self, session: Session = db.session):
        self._session = session


    def add(self, user: User) -> None:
        logger.debug(f"Attempting to add user to session: {user.username} ({user.email})")

        user_db = user.to_orm()
        try:
            self._session.add(user_db)
            self._session.flush()  # Flush to catch IntegrityErrors early if desired, but commit is usually external
            logger.info(f"User '{user.username}' added to session.")
        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Repository: Database error adding/flushing project '{user.username}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to add user '{user.username}' to the database session.")
        except Exception as e:
            logger.error(f"Error adding user '{user.username}' to session: {e}", exc_info=True)
            raise

    def get_by_id(self, user_identificator: str) -> Optional[User]:
        logger.debug(f"Attempting to get user by id: {user_identificator}")
        stmt = select(UserDB).where(UserDB.identificator == user_identificator)
        user_db = self._session.execute(stmt).scalar_one_or_none() 

        if user_db:
            logger.info(f"User found by id: {user_identificator}")
            return User.from_orm(user_db)
        else:
            logger.warning(f"User not found by id: {user_identificator}")
            # raise UserNotFoundError(user_identificator=user_identificator)
            return None

    def get_by_email(self, email: str) -> Optional[User]:
        logger.debug(f"Attempting to get user by email: {email}")
        stmt = select(UserDB).where(UserDB.email == email)
        user_db = self._session.execute(stmt).scalar_one_or_none()

        if user_db:
            logger.info(f"User found by email: {email}")
            return User.from_orm(user_db)
        else:
            logger.warning(f"User not found by email: {email}")
            # raise UserNotFoundError(email=email)
            return None

    def get_by_username(self, username: str) -> Optional[User]:
        logger.debug(f"Attempting to get user by username: {username}")
        stmt = select(UserDB).where(UserDB.username == username)
        user_db = self._session.execute(stmt).scalar_one_or_none()

        if user_db:
            logger.info(f"User found by username: {username}")
            return User.from_orm(user_db)
        else:
            logger.warning(f"User not found by username: {username}")
            # raise UserNotFoundError(email=email)
            return None
    



    # Nao vi ainda =================



    def list_all(self) -> List[User]:
        """
        Retrieves all User records from the database using SQLAlchemy 2.0 select.

        Returns:
            A list of User domain model instances.
        """
        logger.debug("Attempting to list all users")
        stmt = select(UserDB)
        all_users_db = self._session.execute(stmt).scalars().all() # Gets list of ORM objects
        users = [self._map_to_domain(user_db) for user_db in all_users_db]
        logger.info(f"Retrieved {len(users)} users.")
        return users

    def update(self, user: User) -> None:
        """
        Updates an existing User in the database session.
        Finds the user by identificator and updates its attributes.
        Changes are tracked by the session and committed externally.

        Args:
            user: The User domain model instance with updated data.

        Raises:
            UserNotFoundError: If the user to update is not found.
            UsernameAlreadyExists: If trying to change to an existing username upon flush/commit.
            EmailAlreadyExists: If trying to change to an existing email upon flush/commit.
            Exception: For other database errors.
        """
        logger.debug(f"Attempting to update user in session: {user.identificator}")
        # First, find the existing user_db managed by the session
        stmt = select(UserDB).where(UserDB.identificator == user.identificator)
        user_db = self._session.execute(stmt).scalar_one_or_none()

        if not user_db:
            logger.warning(f"User not found for update: {user.identificator}")
            raise UserNotFoundError(user_identificator=user.identificator)

        # Update attributes on the managed object
        user_db.username = user.username
        user_db.email = user.email
        # Only update password if it's different (user.password is already hashed)
        if user_db.password != user.password:
             user_db.password = user.password
             logger.info(f"Password updated in session for user: {user.identificator}")
        user_db.active = user.active

        try:
            # Flush to catch IntegrityErrors early if desired, but commit is usually external
            self._session.flush()
            logger.info(f"User '{user.username}' ({user.identificator}) updated in session.")
        except IntegrityError as e:
            # self._session.rollback() # Mantenha comentado se o rollback é feito externamente (na service)
            error_info = str(e.orig).lower() if e.orig else str(e).lower()
            logger.debug(f"IntegrityError caught in update. error_info: {error_info}") # Log para depuração

            # Verificar especificamente pelo erro de entrada duplicada do MySQL (1062)
            # O padrão é algo como "(1062, "duplicate entry '...' for key '...'")"
            is_duplicate_entry = 'duplicate entry' in error_info and '1062' in error_info

            if is_duplicate_entry:
                # Verificar qual chave causou a duplicação (combine com o nome da constraint/key no erro)
                if 'users.username' in error_info: # Use o nome exato da chave/constraint do erro
                    logger.warning(f"Update failed: Username '{user.username}' likely already exists (Duplicate Entry).")
                    raise UsernameAlreadyExists() from e
                elif 'users.email' in error_info: # Use o nome exato da chave/constraint do erro para email
                    logger.warning(f"Update failed: Email '{user.email}' likely already exists (Duplicate Entry).")
                    raise EmailAlreadyExists() from e
                else:
                    # Erro de duplicidade, mas não identificamos a chave específica
                    logger.warning(f"Update failed due to unrecognized duplicate entry constraint: {error_info}")
                    # Decida se quer levantar uma exceção genérica ou deixar cair no erro abaixo
                    pass # Deixa cair no logger.error genérico abaixo por enquanto

            # Se não for um erro de duplicidade reconhecido ou a chave específica não foi encontrada acima
            logger.error(f"Database integrity error updating user '{user.username}': {e}", exc_info=True)
            raise # Re-levanta a exceção original IntegrityError
        except Exception as e:
            # self._session.rollback()
            logger.error(f"Error updating user '{user.username}' in session: {e}", exc_info=True)
            raise

    def delete(self, user_identificator: str) -> bool:
        """
        Marks a User for deletion in the database session by its identificator.
        Deletion occurs upon external commit.

        Args:
            user_identificator: The UUID string of the user to delete.

        Returns:
            True if the user was found and marked for deletion, False otherwise.

        Raises:
            Exception: For database errors during the process.
        """
        logger.debug(f"Attempting to delete user from session by id: {user_identificator}")
        # Find the user to delete
        stmt = select(UserDB).where(UserDB.identificator == user_identificator)
        user_db = self._session.execute(stmt).scalar_one_or_none()

        if user_db:
            try:
                self._session.delete(user_db)
                # Flush to catch potential errors early, but commit is external
                self._session.flush()
                logger.info(f"User '{user_db.username}' ({user_identificator}) marked for deletion in session.")
                return True
            except Exception as e:
                # self._session.rollback()
                logger.error(f"Error marking user '{user_db.username}' for deletion: {e}", exc_info=True)
                raise
        else:
            logger.warning(f"User not found for deletion: {user_identificator}")
            return False


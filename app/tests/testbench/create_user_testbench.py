import uuid
from app import create_app
from app.models.user import User
from app.infra.repository.user_repository import UserRepository
from app.infra.db import db
from app.models.exceptions import UsernameAlreadyExists, EmailAlreadyExists, UserValidationError
from app.utils.logger import logger

test_username = f"testuser_{uuid.uuid4().hex[:8]}"
test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
test_password = "Password123"
test_identificator = f"{uuid.uuid4()}"

app = create_app()


with app.app_context():
    logger.info("--- Starting User Creation Testbench ---")
    logger.info(f"Attempting to create user: {test_username} ({test_email})")

    try:
        user_repo = UserRepository()
        logger.info("UserRepository instantiated.")

   
        user_domain_object = User(
            identificator=test_identificator,
            username=test_username,
            email=test_email,
            password=test_password
            # 'active' defaults to True
            # 'hashed' defaults to False, so password setter will hash it
        )
        logger.info(f"User domain object created with ID: {user_domain_object.identificator}")
        logger.debug(f"Hashed password preview (first 10 chars): {user_domain_object.password[:10]}...") # Don't log full hash ideally

     
        user_repo.add(user_domain_object)
        logger.info(f"User '{user_domain_object.username}' added to session via repository.")

 
        db.session.commit()
        logger.info(f"Transaction committed. User '{user_domain_object.username}' should be in the database.")

      
        created_user = user_repo.get_by_id(test_identificator)
        if created_user:
            logger.info(f"Verification successful: Found user '{created_user.username}' by ID.")
            assert created_user.email == test_email
            assert created_user.verify_password(test_password)
            logger.info("Password verification successful.")

            created_user.username = "teclado"
            user_repo.update(created_user)
            db.session.commit()
            logger.info(f"User '{created_user.username}' updated in the database.")
            
        else:
            logger.error("Verification failed: Could not retrieve the created user by ID.")

    except (UsernameAlreadyExists, EmailAlreadyExists, UserValidationError) as e:
        db.session.rollback()
        logger.error(f"Failed to create user: {e}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred: {e}", exc_info=True) # Log traceback

    finally:
        logger.info("--- User Creation Testbench Finished ---")


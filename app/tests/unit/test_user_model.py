import pytest
import bcrypt
from app.models.user import User
from app.models.exceptions import UserValidationError, InvalidCreatePasswordError

def test_create_user():
    user = User(1, "testuser", "test@example.com", "Password123")
    
    assert user.identificator == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.status == "active"
    assert user.password is not None  # Deve conter um hash gerado

def test_create_user_with_hashed_password():
    hashed_password = bcrypt.hashpw("Password123".encode(), bcrypt.gensalt()).decode()
    user = User(2, "hasheduser", "hashed@example.com", hashed_password, hashed=True)
    
    assert user._password == hashed_password

def test_invalid_username():
    with pytest.raises(UserValidationError, match="Username cannot be empty."):
        User(3, "", "test@example.com", "Password123")

def test_email_setter_valid_email():
    """Testa se um email válido é aceito."""
    user = User(1, "testuser", "user@example.com", "Password123")
    assert user.email == "user@example.com"

def test_email_setter_empty_email():
    """Testa se um erro é levantado ao definir um email vazio."""
    user = User(1, "testuser", "user@example.com", "Password123")
    with pytest.raises(UserValidationError, match="Email cannot be empty."):
        user.email = ""

def test_email_setter_invalid_email():
    """Testa se um erro é levantado ao definir um email sem '@'."""
    user = User(1, "testuser", "user@example.com", "Password123")
    with pytest.raises(UserValidationError, match="Invalid email format."):
        user.email = "invalidemail.com"

def test_invalid_password_too_short():
    with pytest.raises(InvalidCreatePasswordError, match="Password must be at least 6 characters long."):
        User(4, "user4", "user4@example.com", "abc")

def test_invalid_password_missing_letter():
    with pytest.raises(InvalidCreatePasswordError, match="The password must contain at least one letter."):
        User(5, "user5", "user5@example.com", "123456")

def test_invalid_password_missing_number():
    with pytest.raises(InvalidCreatePasswordError, match="The password must contain at least one number."):
        User(6, "user6", "user6@example.com", "abcdef")

def test_password_hashing():
    user = User(7, "testuser7", "user7@example.com", "Secure123")
    assert user._password != "Secure123"  # Deve ser um hash e não a senha original

def test_verify_password():
    user = User(8, "testuser8", "user8@example.com", "TestPass123")
    
    assert user.verify_password("TestPass123") is True
    assert user.verify_password("WrongPass") is False

def test_invalid_status():
    with pytest.raises(UserValidationError, match="Invalid status. Choose one: active."):
        User(9, "testuser9", "user9@example.com", "Password123", status="inactive")

def test_to_dict():
    user = User(10, "testuser10", "user10@example.com", "Password123")
    user_dict = user.to_dict()
    
    assert user_dict == {
        "identificator": 10,
        "username": "testuser10",
        "email": "user10@example.com",
        "status": "active",
        "password": user.password
    }    

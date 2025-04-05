from app.services.auth_service import AuthService
from flask import jsonify, make_response
from ..models.exceptions import UserNotFoundError, InvalidPasswordError, UsernameAlreadyExists, EmailAlreadyExists, InvalidCreatePasswordError, UserValidationError
from ..utils.logger import logger


class AuthController():
    def __init__(self):
        self.service = AuthService()


    def create_user(self, data):
        user_email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        
        try:
            self.service.create_user(user_email=user_email, username=username, password=password)

            return jsonify({
                "success": True,
                "message": "Account created successfully",
                "data": None,
                "error": None
            }), 201
        
        except UsernameAlreadyExists as e:
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {
                    "code": 400,
                    "type": "UsernameAlreadyExists",
                    "details": str(e)
                }
            }), 400
        except EmailAlreadyExists as e:
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {
                    "code": 400,
                    "type": "EmailAlreadyExists",
                    "details": str(e)
                }
            }), 400
        except InvalidCreatePasswordError as e:
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {
                    "code": 400,
                    "type": "InvalidCreatePasswordError",
                    "details": str(e)
                }
            }), 400
        except UserValidationError as e:
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {
                    "code": 400,
                    "type": "UserValidationError",
                    "details": str(e)
                }
            }), 400
        except Exception as e:   
            return jsonify({
                "success": False,
                "message": "Something went wrong. Please try again later.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "details": str(e)
                }
            }), 500
        

    def login(self, data):
        user_email = data.get('email')
        password = data.get('password')

        try:
            token = self.service.login(user_email, password)
            response = make_response(jsonify({
                "success": True,
                "message": "Login realizado com sucesso",
                "data": None, 
                "error": None
            }), 200)
            response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict')
            return response
        except (UserNotFoundError, InvalidPasswordError):
            return jsonify({
                "success": False,
                "message": "Invalid credentials",
                "data": None,
                "error": {
                    "code": 401,
                    "type": "InvalidCredentials",
                    "details": "Invalid Password and/or E-mail"
                }
            }), 401
        except Exception as e:   
            return jsonify({
                "success": False,
                "message": "Something went wrong. Please try again later.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "details": str(e)
                }
            }), 500
        

from functools import wraps
from flask import request, current_app, redirect, url_for, jsonify
import jwt
from app.repository.user_record import UserRecord  # Classe que manipula os usuários


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("auth_token")

        if not token:
            # request.auth_status = 401  
            # return jsonify({"error": "unauthorized"}), 401
            return redirect(url_for("home.home"))
        
        else:
            try:
                secret_key = current_app.config["SECRET_KEY"]

                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_id = payload.get("id")

                user_record = UserRecord()
                user = user_record.get_user_by_id(user_id)

                request.current_user = user  

            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                # request.auth_status = 401  
                # return jsonify({"error": "Invalid or expired token"}), 401
                return redirect(url_for("home.home"))

        return f(*args, **kwargs)

    return decorated_function


def redirect_if_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("auth_token")

        if token:
            try:
                secret_key = current_app.config["SECRET_KEY"]
                jwt.decode(token, secret_key, algorithms=["HS256"])
                return redirect(url_for("task.tasks_route"))  # Se autenticado, redireciona para /task
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                pass  # Token inválido ou expirado, continua para a home normalmente

        return f(*args, **kwargs)

    return decorated_function
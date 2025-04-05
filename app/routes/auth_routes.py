from flask import Blueprint, request, render_template, redirect, url_for, make_response, jsonify
from app.controllers.auth_controller import AuthController
from ..utils.auth_decorator import redirect_if_logged_in, login_required


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
auth_controller = AuthController()


@auth_bp.route("/login", methods=["POST"])
@redirect_if_logged_in
def login_route():
    data = request.get_json()
    return auth_controller.login(data)

@auth_bp.route("/register", methods=["GET"])
@redirect_if_logged_in
def register_route():
    return render_template("register.html")


@auth_bp.route("/register/create_account", methods=["POST"])
@redirect_if_logged_in
def create_account_route():
    data = request.get_json()
    return auth_controller.create_user(data)
     

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout_route():
    response = make_response(jsonify({"message": "Logout realizado com sucesso"}))
    response.set_cookie("auth_token", "", expires=0,  httponly=True, secure=True, samesite='Strict')  # Remove o cookie
    return response
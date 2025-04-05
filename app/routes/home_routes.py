from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..utils.auth_decorator import redirect_if_logged_in

home_bp = Blueprint("home", __name__, url_prefix="/")


@home_bp.route("/", methods=["GET"])
@redirect_if_logged_in
def home():
    return render_template("home.html")

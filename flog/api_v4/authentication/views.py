from apiflask import APIBlueprint, abort
from authlib.jose import jwt
from functools import wraps
from flask import request, current_app, g
from flask_cors import CORS
from .schemas import LoginSchema, RegisterSchema
from ...models import User
from ...extensions import db, auth


# create authentication blueprint for API v4
auth_bp = APIBlueprint("auth", __name__, url_prefix="/v4/auth")
CORS(auth_bp)

@auth.verify_token
def verify_token(token: str):
    """
    verify token and returns user
    """
    user = User.verify_auth_token_api(token)
    if user:
        g.current_user = user
        user.ping()
        return user
    return None


@auth_bp.get("/")
@auth_bp.get("/help/")
def help():
    """
    help API of blueprint
    """
    return {
        "/help": "help API of blueprint",
        "/login": "sign in and get API auth token",
        "/register": "create a new account"
    }


@auth_bp.post("/login/")
@auth_bp.input(LoginSchema, location="form")
def login(data):
    """
    sign in and get API auth token
    """
    expires = int(request.args.get("expires", default=30*3600*24))
    username = data["username"]
    password = data["password"]
    user: User = User.query.filter_by(username=username).first_or_404()
    if user.verify_password(password):
        return {
            "auth_token": user.gen_auth_api_token(expires)
        }, 200
    else:
        abort(403)


@auth_bp.post("/register/")
@auth_bp.input(RegisterSchema, location="form")
def register(data):
    """
    create a new account
    """
    # get form data
    username = data["username"]
    password = data["password"]
    email = data["email"]
    about_me = data["about_me"]
    name = data["name"]

    # check if requested username or email exists
    uu = User.query.filter_by(username=username).first()
    ue = User.query.filter_by(email=email).first()
    if uu:
        return {
            "message": "username already exists"
        }, 400
    if ue:
        return {
            "message": "email already exists"
        }, 400

    # write data into db
    user = User(
        username=username,
        password=password,
        email=email,
        about_me=about_me,
        name=name
    )
    db.session.add(user)
    db.session.commit()
    return {
        "message": "ok"
    }

from apiflask import APIBlueprint, abort
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from flask import current_app
from time import time
from .schemas import LoginSchema, RegisterSchema
from ...models import User
from ...extensions import db, auth


# create authentication blueprint for API v4
auth_bp = APIBlueprint("auth", __name__, url_prefix="/auth")


@auth.verify_token
def verify_token(token: str):
    """
    verify token and returns user
    """
    try:
        data = jwt.decode(token.encode("ascii"), current_app.config["SECRET_KEY"])
        if data.get("time") + 3600 * 24 * 30 > time():
            user = User.query.get(data.get("uid"))  # None if user does not exist
            if (
                user and user.password_update and
                user.password_update > data.get("time")
            ):
                return None
        else:
            raise JoseError("Token expired")
    except JoseError:
        return None
    else:
        user.ping()
        return user


@auth_bp.get("/")
@auth_bp.get("/help")
def help():  # pragma: no cover
    """
    help API of blueprint
    """
    return {
        "/help": "help API of blueprint",
        "/login": "sign in and get API auth token",
        "/register": "create a new account",
    }


@auth_bp.post("/login")
@auth_bp.input(LoginSchema)
def login(data):
    """
    sign in and get API auth token
    """
    username, password = data["username"], data["password"]
    user = User.query.filter_by(username=username).first()
    email = User.query.filter_by(email=username).first()
    if not (user or email):
        abort(404)

    user = user or email
    if not user.verify_password(password):
        abort(403)
    return {"auth_token": "Bearer " + user.auth_token()}, 200


@auth_bp.post("/register")
@auth_bp.input(RegisterSchema)
def register(data):
    """
    create a new account
    """
    u = User()
    for key, value in data.items():
        if key == "password":
            u.set_password(value)
            continue
        elif key == "username" and User.query.filter_by(username=value).first():
            return {"message": "username already exists"}, 400
        elif key == "email" and User.query.filter_by(email=value).first():
            return {"message": "email already exists"}, 400
        setattr(u, key, value)

    db.session.add(u)
    db.session.commit()
    return {"message": "ok"}


# TODO: finish these after send_mail has been implemented.
# @auth_bp.get("/confirm/send")
# @auth_bp.auth_required
# def send_confirmation():
#     me: User = g.current_user
#     token = me.gen_email_verify_token()
#     send_email(
#         [me.email],
#         "Confirm Your Account",
#         "confirm",
#         username=me.username,
#         token=token,
#         mode=2,
#     )
#     return {"message": "ok"}


# @auth_bp.get("/confirm")
# @auth.login_required
# @auth_bp.input(EmailConfirmationSchema)
# def confirm(data):
#     me: User = g.current_user
#     token = data["token"]
#     if me.verify_email_token(token):
#         return {"message": "ok"}
#     else:
#         return {"message": "failed"}

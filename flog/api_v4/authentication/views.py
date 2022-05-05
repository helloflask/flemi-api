from apiflask import APIBlueprint, abort
from authlib.jose import jwt
from flask import current_app, g, request
from flask_cors import CORS
from time import time
from .schemas import LoginSchema, RegisterSchema, EmailConfirmationSchema
from ...emails import send_email
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
    try:
        data = jwt.decode(token.encode("ascii"), current_app.config["SECRET_KEY"])
        if data.get("time") + 3600 * 24 * 30 > time():
            user: User = User.query.get(data.get("uid"))  # None if user does not exist
            if user.password_update:
                if user.password_update > data.get("time"):
                    return None
        else:
            raise Exception  # trigger "except" to return None
    except:  # either by decoding failure or by token expiration
        return None
    g.current_user = user
    user.ping()
    return user


@auth_bp.get("/")
@auth_bp.get("/help")
def help():
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
    username = data["username"]
    password = data["password"]
    user: User = User.query.filter_by(username=username).first()
    email: User = User.query.filter_by(email=username).first()
    if not (user or email):
        abort(404)
    else:
        user: User = user or email
    if user.verify_password(password):
        return {"auth_token": user.gen_auth_api_token()}, 200
    else:
        abort(403)


@auth_bp.post("/register")
@auth_bp.input(RegisterSchema)
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
        return {"message": "username already exists"}, 400
    if ue:
        return {"message": "email already exists"}, 400

    # write data into db
    user = User(
        username=username,
        password=password,
        email=email,
        about_me=about_me,
        name=name,
        password_update=time(),
    )
    db.session.add(user)
    db.session.commit()
    return {"message": "ok"}


@auth_bp.get("/confirm/send")
@auth.login_required
def send_confirmation():
    me: User = g.current_user
    token = me.gen_email_verify_token()
    send_email(
        [me.email],
        "Confirm Your Account",
        "confirm",
        username=me.username,
        token=token,
        mode=2,
    )
    return {"message": "ok"}


@auth_bp.get("/confirm")
@auth.login_required
@auth_bp.input(EmailConfirmationSchema)
def confirm(data):
    me: User = g.current_user
    token = data["token"]
    if me.verify_email_token(token):
        return {"message": "ok"}
    else:
        return {"message": "failed"}

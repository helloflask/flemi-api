from apiflask import APIBlueprint, abort
from authlib.jose import jwt
from flask import request
from flask_cors import CORS
from time import time
from ...models import User


# create authentication blueprint for API v4
api_auth_bp = APIBlueprint("api_v4_auth", __name__, url_prefix="/api/v4/auth/")
CORS(api_auth_bp)


def private_key():
    with open("jwtRS256.key", "rb") as f:
        key = f.read()
    return key


def public_key():
    with open("jwtRS256.key.pub", "rb") as f:
        key = f.read()
    return key


@api_auth_bp.get("/")
def index():
    return {
        "/login": "Log in to a user"
    }


@api_auth_bp.post("/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user: User = User.query.filter_by(username=username).first_or_404()
    if user.verify_password(password):
        header = {"alg": "RS256"}
        payload = {
            "uid": user.id,
            "expires": time()
        }
        token = jwt.encode(header, payload, private_key())
        return {"auth_token": token}, 200
    else:
        abort(403)

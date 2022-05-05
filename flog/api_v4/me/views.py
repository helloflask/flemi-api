from apiflask import APIBlueprint
from flask import g
from .schemas import BasicProfileEditSchema, AvatarEditSchema, AboutEditSchema
from ..schemas import PrivateUserOutputSchema
from ...extensions import auth, db
from ...models import User


me_bp = APIBlueprint("me", __name__, url_prefix="/v4/me")


@me_bp.get("/")
@auth.login_required
@me_bp.output(PrivateUserOutputSchema)
def self_profile():
    """
    profile of the current user
    """
    me: User = g.current_user
    return me


@me_bp.get("/help")
def help():
    """
    help API of blueprint
    """
    return {
        "/": "profile of the current user",
        "/edit/basic/": "edit username, email and name",
        "/edit/avatar/": "change avatar",
        "/help/": "help API of blueprint",
    }


@me_bp.post("/edit/basic")
@auth.login_required
@me_bp.input(BasicProfileEditSchema)
def edit_basic(data):
    """
    edit username, email and name
    """
    me: User = g.current_user
    username = data["username"]
    email = data["email"]
    name = data["name"]
    if User.query.filter_by(username=username).first():
        return {"message": "username already exists"}, 400
    if User.query.filter_by(email=email).first():
        return {"message": "email already exists"}, 400
    me.username = username
    me.email = email
    me.name = name
    db.session.commit()
    return {"message": "ok"}, 200


@me_bp.post("/edit/avatar")
@auth.login_required
@me_bp.input(AvatarEditSchema)
def edit_avatar(data):
    """
    change avatar
    """
    me: User = g.current_user
    me.custom_avatar_url = data["avatar_url"]
    db.session.commit()
    return {"message": "ok"}, 200


@me_bp.post("/edit/about")
@auth.login_required
@me_bp.input(AboutEditSchema)
def edit_about_me(data):
    """
    edit self description
    """
    me: User = g.current_user
    me.about_me = data["about_me"]
    db.session.commit()
    return {"message": "ok"}, 200

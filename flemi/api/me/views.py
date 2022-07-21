from apiflask import APIBlueprint

from ...extensions import auth
from ...extensions import db
from ...models import User
from .schemas import AboutEditSchema
from .schemas import AvatarEditSchema
from .schemas import BasicProfileEditSchema
from .schemas import PrivateUserOutputSchema


me_bp = APIBlueprint("me", __name__, url_prefix="/me")


@me_bp.get("")
@me_bp.auth_required(auth)
@me_bp.output(PrivateUserOutputSchema)
def self_profile():
    """
    profile of the current user
    """
    return auth.current_user


@me_bp.get("/help")
def help():  # pragma: no cover
    """
    help API of blueprint
    """
    return {
        "/": "profile of the current user",
        "/edit/basic": "edit username, email and name",
        "/edit/avatar": "change avatar",
        "/help": "help API of blueprint",
    }


@me_bp.put("/edit/basic")
@me_bp.auth_required(auth)
@me_bp.input(BasicProfileEditSchema(partial=True))
def edit_basic(data):
    """
    edit username, email and name
    """
    me: User = auth.current_user
    for key, value in data.items():
        if (
            key == "username" and User.query.filter_by(username=value).first()
        ):  # pragma: no cover
            return {"message": "username already exists"}, 400
        if (
            key == "email" and User.query.filter_by(email=value).first()
        ):  # pragma: no cover
            return {"message": "email already exists"}, 400
        setattr(me, key, value)

    db.session.commit()
    return {"message": "ok"}, 200


@me_bp.put("/edit/avatar")
@me_bp.auth_required(auth)
@me_bp.input(AvatarEditSchema)
def edit_avatar(data):
    """
    change avatar
    """
    auth.current_user.custom_avatar_url = data["avatar_url"]
    db.session.commit()
    return {"message": "ok"}, 200


@me_bp.put("/edit/about")
@me_bp.auth_required(auth)
@me_bp.input(AboutEditSchema)
def edit_about_me(data):
    """
    edit self description
    """
    auth.current_user.about_me = data["about_me"]
    db.session.commit()
    return {"message": "ok"}, 200

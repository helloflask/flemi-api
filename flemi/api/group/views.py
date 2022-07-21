from apiflask import APIBlueprint
from flask import request

from ...models import Group
from ..auth.views import auth
from ..auth.views import verify_token
from .schemas import GroupOutSchema

group_bp = APIBlueprint("group", __name__, url_prefix="/group")


@group_bp.get("/all")
@group_bp.output(GroupOutSchema(many=True))
def all():
    token = request.headers.get("Authorization", "")
    public_groups = Group.query.filter_by(private=False).all()

    try:
        token = token[7:]
        user = verify_token(token)
    except IndexError:
        return public_groups

    if user is None:
        return public_groups
    else:
        return [g for g in Group.query.all() if not g.private or user in g.members]


@group_bp.get("/me")
@group_bp.auth_required(auth)
@group_bp.output(GroupOutSchema(many=True))
def me():
    return auth.current_user.groups

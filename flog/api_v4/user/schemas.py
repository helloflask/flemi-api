from apiflask import Schema
from apiflask.fields import (
    Integer,
    Boolean,
    String,
    DateTime,
)
from flog.extensions import ma


class PublicUserOutSchema(Schema):
    id = Integer()
    username = String()
    name = String()
    location = String()
    about_me = String()
    confirmed = Boolean()
    blocked = Boolean()
    member_since = DateTime()
    last_seen = DateTime()
    self = ma.URLFor("user.user", values=dict(user_id="<id>"))  # type: ignore

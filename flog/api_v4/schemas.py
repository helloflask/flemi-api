from apiflask import Schema
from apiflask.fields import (
    Integer,
    Boolean,
    String,
    DateTime,
    Email,
    Float
)


class PrivateUserOutputSchema(Schema):
    id = Integer()
    email = Email()
    username = String()
    name = String()
    coins = Float()
    experience = Integer()
    location = String()
    about_me = String()
    confirmed = Boolean()
    blocked = Boolean()
    member_since = DateTime()
    last_seen = DateTime()
    is_admin = Boolean()
    remote_addr = String()
    clicks = Integer()
    clicks_today = Integer()

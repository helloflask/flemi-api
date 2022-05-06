from marshmallow import Schema, validate
from marshmallow.fields import Integer, Float, Boolean, DateTime, String, Email, Url


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


class BasicProfileEditSchema(Schema):
    username = String(
        required=True, validate=validate.Regexp("^[A-Za-z]([A-Za-z0-9_\-.]){2,15}$", 0)
    )
    email = Email(required=True)
    name = String(required=True, validate=validate.Length(1, 64))


class AvatarEditSchema(Schema):
    avatar_url = Url()


class AboutEditSchema(Schema):
    about_me = String(validate=validate.Length(0, 250))

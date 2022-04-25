from marshmallow import Schema, validate
from marshmallow.fields import String, Email, Url


class BasicProfileEditSchema(Schema):
    username = String(
        required=True,
        validate=validate.Regexp(
            "^[A-Za-z]([A-Za-z0-9_\-.]){2,15}$", 0
        )
    )
    email = Email(required=True)
    name = String(
        required=True,
        validate=validate.Length(1, 64)
    )


class AvatarEditSchema(Schema):
    avatar_url = Url()


class AboutEditSchema(Schema):
    about_me = String(
        validate=validate.Length(0, 250)
    )

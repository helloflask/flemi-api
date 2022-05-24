from marshmallow import Schema, validate
from marshmallow.fields import Function, String, Email, Url


class PrivateUserOutputSchema(Schema):
    avatar_url = Function(lambda obj: obj.avatar_url())

    class Meta:
        fields = (
            "id",
            "email",
            "username",
            "name",
            "coins",
            "experience",
            "location",
            "about_me",
            "confirmed",
            "blocked",
            "member_since",
            "last_seen",
            "is_admin",
            "clicks",
            "clicks_today",
            "avatar_url",
        )


class BasicProfileEditSchema(Schema):
    username = String(
        required=True, validate=validate.Regexp("^[A-Za-z]([A-Za-z0-9_\-.]){2,15}$", 0)
    )
    email = Email(required=True)
    name = String(required=True, validate=validate.Length(1, 64))


class AvatarEditSchema(Schema):
    avatar_url = Url(required=True)


class AboutEditSchema(Schema):
    about_me = String(validate=validate.Length(0, 250))

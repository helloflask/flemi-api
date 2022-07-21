from apiflask import Schema
from apiflask.fields import Email
from apiflask.fields import String
from marshmallow import validate


class LoginSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class RegisterSchema(Schema):
    username = String(
        required=True, validate=validate.Regexp(r"^[A-Za-z]([A-Za-z0-9_\-.]){2,15}$", 0)
    )
    password = String(required=True)
    email = Email(required=True)
    about_me = String()
    name = String(required=True)


# class EmailConfirmationSchema(Schema):
#     token = String(required=True)

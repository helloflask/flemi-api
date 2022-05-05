from apiflask import Schema
from apiflask.fields import String, Email
from marshmallow import validate


class LoginSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class RegisterSchema(Schema):
    username = String(
        required=True, validate=validate.Regexp("^[A-Za-z]([A-Za-z0-9_\-.]){5,11}$", 0)
    )
    password = String(required=True)
    email = Email(required=True)
    about_me = String()
    name = String(required=True)


class EmailConfirmationSchema(Schema):
    token = String(required=True)

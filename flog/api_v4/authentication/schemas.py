from apiflask import Schema
from apiflask.fields import String


class LoginSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class RegisterSchema(Schema):
    username = String(required=True)
    password = String(required=True)
    email = String(required=True)
    about_me = String()
    name = String(required=True)

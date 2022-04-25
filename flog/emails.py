from flask_mail import Message
from flask import render_template
from .extensions import mail


def send_email(recipients: list, subject=None, template=None, **kwargs):
    pass  # will add

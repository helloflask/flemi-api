"""
MIT License
Copyright (c) 2020 Andy Zhou
"""

import os
from os.path import abspath
from os.path import dirname
from os.path import join


def generate_sqlite_filename(filename: str):
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return "sqlite:///" + os.path.join(basedir, f"{filename}.sqlite3")


class Base:
    DEBUG = False
    TESTING = False
    SSL_REDIRECT = False

    SECRET_KEY = os.getenv("SECRET_KEY", "hard-to-guess")

    SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 10, "pool_size": 30}
    # SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.getenv("FLEMI_EMAIL", "flemi_admin@example.com")
    MAIL_PASSWORD = os.getenv("FLEMI_EMAIL_PASSWORD", "flemi_email_password")
    MAIL_DEFAULT_SENDER = os.getenv(
        "DEFAULT_EMAIL_SENDER", "flemi <flemi_admin@example.com>"
    )

    HOT_POST_COIN = 7
    HOT_COLUMN_COIN = 40

    FLEMI_ADMIN = os.getenv("FLEMI_ADMIN", "flemi_admin")
    FLEMI_ADMIN_EMAIL = os.getenv("FLEMI_ADMIN_EMAIL", MAIL_USERNAME)
    FLEMI_ADMIN_PASSWORD = os.getenv("FLEMI_ADMIN_PASSWORD", "hydrogen")

    LOCALES = {"en_US": "English(US)", "zh_Hans_CN": "简体中文"}

    UPLOAD_DIRECTORY = join(dirname(dirname(abspath(__file__))), "images/")
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    CKEDITOR_HEIGHT = 800
    CKEDITOR_WIDTH = 1024
    CKEDITOR_FILE_UPLOADER = "image.upload"
    CKEDITOR_ENABLE_CSRF = True

    # Specially configured for pythonanywhere
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 280}

    # Allowed tags for posts
    # fmt: off
    FLEMI_ALLOWED_TAGS = [
        "p", "hr", "h1", "h2", "h3", "h4", "a",
        "img", "strong", "em", "s", "i", "b",
        "div", "span", "br", "ol", "ul", "li",
        "table", "thead", "tbody", "th", "td", "tr",
        "pre", "code", "iframe", "sub", "sup",
        "quote", "blockquote", "small"
    ]

    FLEMI_ALLOWED_HTML_ATTRIBUTES = [
        "href", "src", "style", "class",
        "xmlns:xlink", "width", "height", "tabindex",
        "viewBox", "role", "focusable", "stroke-width",
        "id", "d", "lang", "alt"
    ]

    # fmt: on

    @classmethod
    def init_app(cls, app):
        pass


class Production(Base):
    FLASK_CONFIG = "production"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_PROD", generate_sqlite_filename("data")
    )

    @classmethod
    def init_app(cls, app):
        Base.init_app(app)

        import logging
        from logging.handlers import SMTPHandler

        credentials = None
        secure = None
        if getattr(cls, "ADMIN_EMAIL", None) is not None:
            credentials = (cls.FLEMI_ADMIN_EMAIL, cls.MAIL_PASSWORD)
            if getattr(cls, "MAIL_USE_TLS", None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_DEFAULT_SENDER,
            toaddrs=[cls.FLEMI_ADMIN_EMAIL],
            subject="Application Error",
            credentials=credentials,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class Development(Base):
    FLASK_CONFIG = "development"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_DEV", generate_sqlite_filename("data-dev")
    )
    DEBUG = True
    MAIL_SUPPRESS_SEND = True


class Test(Base):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_TEST", "sqlite:///:memory:")


config = {
    "production": Production,
    "development": Development,
    "testing": Test,
}

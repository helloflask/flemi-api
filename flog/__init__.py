from apiflask import APIFlask
from flask import Flask
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from .extensions import (
    db,
    login_manager,
    migrate
)
from .commands import register_commands
from .models import User, Post, Group, Message, Column
from .settings import config
from . import api_v4


def create_app(config_name=None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")
    app = APIFlask("flog-api")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)
    register_config(app=app, config_name="development")
    register_extensions(app=app, db=db)
    register_blueprints(app=app)
    register_commands(app=app, db=db)
    return app


def register_config(app: Flask, config_name: str) -> None:
    app.config.from_object(config[config_name])


def register_extensions(app: Flask, db) -> None:
    db.init_app(app=app)
    login_manager.init_app(app=app)
    migrate.init_app(app=app, db=db)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(api_v4.auth_bp)
    app.register_blueprint(api_v4.me_bp)


def register_context(app: Flask) -> None:
    @app.shell_context_processor
    def make_shell_context():
        return dict(
            db=db,
            User=User,
            Post=Post,
            Group=Group,
            Message=Message,
            Column=Column
        )

import importlib as il
import os

from apiflask import APIFlask
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from .commands import register_commands
from .extensions import db
from .extensions import ma
from .extensions import migrate
from .models import Column
from .models import Group
from .models import Message
from .models import Post
from .models import User
from .settings import config
from .utils import get_all_remote_addr


def create_app(config_name=None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")
    app = APIFlask("flemi")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)

    @app.get("/")
    def index():
        """
        help API of the app
        """
        return {"/": "version 4.x of flemi web API"}

    register_config(app, config_name)
    register_blueprints(app)
    register_extensions(app)
    register_commands(app, db)
    register_context(app)
    return app


def register_config(app: Flask, config_name: str) -> None:
    app.config.from_object(config[config_name])


def register_extensions(app: Flask) -> None:
    db.init_app(app=app)
    migrate.init_app(app=app, db=db)
    ma.init_app(app)


def register_blueprints(app: Flask) -> None:
    for mod_name in ("auth", "me", "post", "user", "group"):
        mod = il.import_module(f".api.{mod_name}.views", "flemi")
        blueprint = getattr(mod, f"{mod_name}_bp")
        CORS(blueprint)
        app.register_blueprint(blueprint)


def register_context(app: Flask) -> None:
    @app.shell_context_processor
    def make_shell_context():
        return dict(
            db=db,
            User=User,
            Post=Post,
            Group=Group,
            Message=Message,
            Column=Column,
            get_all_remote_addr=get_all_remote_addr,
        )

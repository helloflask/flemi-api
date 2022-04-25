from apiflask import HTTPTokenAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail


db = SQLAlchemy()
migrate = Migrate()
auth = HTTPTokenAuth()
mail = Mail()

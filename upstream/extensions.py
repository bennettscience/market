from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from htmx_flask import Htmx
import jinja_partials as partials
from sqlalchemy import MetaData

db = SQLAlchemy()
htmx = Htmx()
login_manager = LoginManager()
marshmallow = Marshmallow()
migrate = Migrate()

convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
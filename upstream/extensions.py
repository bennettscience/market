from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from htmx_flask import Htmx
import jinja_partials as partials

db = SQLAlchemy()
htmx = Htmx()
login_manager = LoginManager()
marshmallow = Marshmallow()
migrate = Migrate()

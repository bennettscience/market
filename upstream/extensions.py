from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from htmx_flask import Htmx

db = SQLAlchemy()
htmx = Htmx()
marshmallow = Marshmallow()
migrate = Migrate()

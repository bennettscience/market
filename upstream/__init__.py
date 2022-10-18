from flask import Flask

from upstream.extensions import db, htmx, marshmallow, migrate
from upstream.blueprints import event, item, user


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

    db.init_app(app)
    migrate.init_app(app, db)
    htmx.init_app(app)
    marshmallow.init_app(app)

    app.register_blueprint(event.bp)
    app.register_blueprint(item.bp)
    app.register_blueprint(user.bp)

    return app

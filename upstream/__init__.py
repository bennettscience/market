from flask import Flask

from upstream.extensions import db, htmx, login_manager, marshmallow, migrate, partials
from upstream.blueprints import event, home, item, transaction, user


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SECRET_KEY"] = "mysupersecretkey"

    db.init_app(app)
    migrate.init_app(app, db)
    htmx.init_app(app)
    login_manager.init_app(app)
    marshmallow.init_app(app)

    partials.register_extensions(app)

    app.register_blueprint(event.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(item.bp)
    app.register_blueprint(transaction.bp)
    app.register_blueprint(user.bp)

    @app.cli.command("setup")
    def setup():
        from upstream.models import Item

        items = [
            "Potato",
            "Broccoli",
            "Green Pepper",
            "Garlic",
            "Pickling Cucumber",
            "Slicer Cucumber",
            "Salad",
        ]
        data = [Item(name=item) for item in items]
        db.session.add_all(data)
        db.session.commit()

    return app

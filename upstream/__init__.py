from flask import Flask, send_from_directory

from upstream.extensions import db, htmx, login_manager, marshmallow, migrate, partials
from upstream.blueprints import event, home, item, transaction, user


def create_app(config):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config)

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

    @app.route('/manifest.json')
    def mainfest():
        return send_from_directory('static', 'manifest.json')

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

from flask import Blueprint

from upstream.extensions import db
from upstream.models import User

bp = Blueprint("user", __name__)


@bp.route("/users/<string:name>")
def create(name):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()

    return "Created user!"

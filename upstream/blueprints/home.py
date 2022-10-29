from flask import Blueprint, render_template

from upstream.models import Event

bp = Blueprint("home", __name__)


@bp.get("/")
def index():
    events = Event.query.order_by(Event.starts.desc()).all()
    return render_template("home/index.html", events=events)

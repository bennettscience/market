from flask import Blueprint, render_template, session
from flask_login import current_user
from htmx_flask import request

from upstream.charts import ChartService
from upstream.models import Event, Item
from upstream.schemas import EventSchema

bp = Blueprint("home", __name__)


@bp.get("/")
def index():

    if not current_user.is_anonymous and session['_fresh']:
        
        events = Event.query.order_by(Event.starts.desc()).all()
        if request.htmx:
            template = "home/index-htmx.html"
        else:
            template = "home/index.html"

        return render_template(template, events=EventSchema(many=True).dump(events))
    else:
        if request.htmx:
            template = "home/login-htmx.html"
        else:
            template = "home/login.html"
    
        return render_template(template)


@bp.get("/stats")
def all_stats():
    pass

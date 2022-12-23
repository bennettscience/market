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
        template = "home/index.html"

        resp_data = {
            "events": EventSchema(many=True).dump(events)
        }

        if request.htmx:
            resp = render_template(template, **resp_data)
        else:
            resp = render_template("shared/layout-wrap.html", partial=template, data=resp_data)

        return resp
    else:
        template = "home/login.html"
        if request.htmx:
            resp = render_template(template)
        else:
            resp = render_template("shared/layout-wrap.html", partial=template, data={})
    
        return resp


@bp.get("/stats")
def all_stats():
    pass

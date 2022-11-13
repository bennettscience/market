from flask import Blueprint, render_template
from htmx_flask import request

from upstream.models import Event, Item
from upstream.schemas import EventSchema

bp = Blueprint("home", __name__)


@bp.get("/")
def index():
    events = Event.query.order_by(Event.starts.desc()).all()
    if request.htmx:
        template = "home/index-htmx.html"
    else:
        template = "home/index.html"

    sales = sum([event.gross_sales() for event in events])
    inventory = len(Item.query.all())
    return render_template(
        template,
        events=EventSchema(many=True).dump(events),
        sales=sales,
        inventory=inventory,
    )

from typing import List

from flask import Blueprint, jsonify, render_template
from htmx_flask import make_response
from webargs import fields
from webargs.flaskparser import parser

from upstream.extensions import db, htmx
from upstream.models import Event, EventItem
from upstream.schemas import EventSchema, ItemSchema

bp = Blueprint("events", __name__)


@bp.get("/events")
def get_events() -> List[Event]:
    events = Event.query.order_by(Event.starts.desc()).all()
    return jsonify(EventSchema(many=True).dump(events))


@bp.get("/events/create")
def get_event_form():
    return make_response(
        render_template(
            "shared/sidebar.html",
            partial="forms/create-event.html",
            push_url="/events/create",
        )
    )


@bp.post("/events")
def post_event() -> List[Event]:
    try:
        args = parser.parse(
            {"name": fields.String(), "starts": fields.DateTime()}, location="form"
        )
        event = Event(**args)
        db.session.add(event)
        db.session.commit()

        return render_template("home/index.html", events=Event.query.all())
    except Exception as e:
        return jsonfiy(e)


@bp.get("/events/<int:id>")
def get_single_event(id: int) -> Event:
    event = Event.query.filter(Event.id == id).first_or_404()
    return jsonify(EventSchema().dump(event))


@bp.put("/events/<int:id>")
def update_single_event(id: int) -> Event:
    # TODO: Add Manager class to Models
    pass


@bp.delete("/events/<int:id>")
def delete_single_event(id: int) -> List[Event]:
    event = Event.query.filter(Event.id == id).first_or_404()
    db.session.delete(event)
    db.session.commit()

    return jsonfiy(EventSchema(many=True).dump(Event.query.all()))


# Event Inventory controls
@bp.post("/events/<int:id>/inventory")
def post_event_inventory(id: int) -> Event:
    # Post an item to the event
    args = parser.parse(
        {"item_id": fields.Int(), "quantity": fields.Int()}, location="form"
    )
    event = Event.query.filter(Event.id == id).first_or_404()

    event_item = EventItem(
        event_id=event.id, item_id=args["item_id"], quantity=args["quantity"]
    )
    db.session.add(event_item)
    db.session.commit()

    return jsonify(EventSchema().dump(event))

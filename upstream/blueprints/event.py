from typing import List

from flask import Blueprint, jsonify, render_template
from htmx_flask import make_response
from sqlalchemy.sql import select, not_
from webargs import fields
from webargs.flaskparser import parser

from upstream.charts import EventChartBuilder, ChartService
from upstream.extensions import db, htmx
from upstream.models import Event, EventItem, Item
from upstream.schemas import EventSchema, EventItemSchema

bp = Blueprint("events", __name__)


@bp.get("/events")
def get_events() -> List[Event]:
    events = Event.query.order_by(Event.starts.desc()).all()
    return jsonify(EventSchema(many=True).dump(events))


@bp.get("/events/create")
def get_event_form():
    return make_response(
        render_template(
            "shared/partials/sidebar.html",
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

        events = Event.query.order_by(Event.starts.desc()).all()

        return render_template(
            "home/index-htmx.html",
            events=EventSchema(many=True).dump(events),
        )
    except Exception as e:
        return jsonify(e)


@bp.get("/events/<int:id>")
def get_single_event(id: int) -> Event:

    event = Event.query.filter(Event.id == id).first_or_404()
    sales = event.gross_sales()

    if event.inventory.all():
        data_builder = EventChartBuilder(event)
        data = data_builder.build()

        service = ChartService(data)
        chart = service.stacked_bar()
    else:
        chart = "No data to display."

    return render_template("events/index.html", event=event, sales=sales, chart=chart)


@bp.put("/events/<int:id>")
def update_single_event(id: int) -> Event:
    # TODO: Add Manager class to Models
    pass


@bp.delete("/events/<int:id>")
def delete_single_event(id: int) -> List[Event]:
    event = Event.query.filter(Event.id == id).first_or_404()
    db.session.delete(event)
    db.session.commit()

    return jsonify(EventSchema(many=True).dump(Event.query.all()))


@bp.get("/events/<int:event_id>/inventory")
def get_inventory_form(event_id):
    # Filter out any items that are already included in the event.
    # https://stackoverflow.com/questions/68454651/python-sqlalchemy-how-to-get-all-items-that-are-not-related-to-current-user

    event_inventory_subq = select(EventItem.item_id).filter(
        EventItem.event_id == event_id
    )
    available_items = (
        db.session.query(Item)
        .filter(not_(Item.id.in_(event_inventory_subq)))
        .order_by(Item.name)
        .all()
    )

    data = {"items": available_items, "event": event_id}
    return render_template(
        "shared/partials/sidebar.html", partial="forms/create-inventory.html", data=data
    )


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


@bp.get("/events/<int:event_id>/inventory/<int:item_id>")
def get_inventory_edit_form(event_id, item_id):
    event = Event.query.filter(Event.id == event_id).first()

    event_item = event.inventory.filter(EventItem.item_id == item_id).first()

    return render_template(
        "shared/partials/sidebar.html",
        partial="forms/edit-inventory.html",
        data=event_item,
    )


@bp.put("/events/<int:event_id>/inventory/<int:item_id>")
def update_event_inventory_item(event_id: int, item_id: int) -> Event:
    # Update the quantity taken to an event
    args = parser.parse({"quantity": fields.Int()}, location="form")
    event = Event.query.filter(Event.id == event_id)
    inventory_item = event.inventory.filter(EventItem.item_id == item_id).first()
    inventory_item.quantity = args["quantity"]
    db.session.commit()

    return make_response(
        render_template="events/index.html", trigger={"showToast": "Quantity updated."}
    )

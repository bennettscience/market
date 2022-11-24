from typing import List

from flask import Blueprint, jsonify, render_template
from htmx_flask import make_response, request
from webargs import fields
from webargs.flaskparser import parser

from upstream.charts import ChartService
from upstream.extensions import db, htmx
from upstream.models import Event, Item
from upstream.schemas import ItemSchema


bp = Blueprint("items", __name__)


@bp.get("/items")
def get_items() -> List[Item]:
    items = Item.query.order_by(Item.name).all()
    return render_template("items/items-table.html", items=items)
    # return jsonify(ItemSchema(many=True).dump(items))


@bp.get("/items/create")
def create_item_form():
    return make_response(
        render_template(
            "shared/partials/sidebar.html",
            partial="forms/create-item.html",
            push_url="/items/create",
        )
    )


@bp.post("/items")
def post_item() -> List[Item]:
    args = parser.parse(ItemSchema(), location="form")
    item = Item(**args)
    db.session.add(item)
    db.session.commit()

    return make_response(
        render_template("/home/index.html", events=Event.query.all()),
        push_url="/",
        trigger={"showToast": "Added item sucecssfully."},
    )


@bp.get("/items/<int:id>")
def get_single_item(id: int) -> Item:
    item = Item.query.filter(Item.id == id).first_or_404()
    
    chart = ChartService()
    # For each event:
        # Get the number of items taken
        # Get the number of items sold
        # Pass into an array
        # https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html
    return render_template("items/item-detail.html", item=item)


# @bp.put("/events/<int:id>")
# def update_single_event(id: int) -> Event:
#     # TODO: Add Manager class to Models
#     pass


@bp.delete("/events/<int:id>")
def delete_single_item(id: int) -> List[Item]:
    item = Item.query.filter(Item.id == id).first_or_404()
    db.session.delete(item)
    db.session.commit()

    return jsonfiy(ItemSchema(many=True).dump(Item.query.all()))

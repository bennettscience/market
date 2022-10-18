from typing import List

from flask import Blueprint, jsonify
from webargs import fields
from webargs.flaskparser import parser

from upstream.extensions import db, htmx
from upstream.models import Item
from upstream.schemas import ItemSchema

bp = Blueprint("items", __name__)


@bp.get("/items")
def get_items() -> List[Item]:
    items = Item.query.all()
    return jsonify(ItemSchema(many=True).dump(items))


@bp.post("/items")
def post_item() -> List[Item]:
    args = parser.parse(ItemSchema(), location="form")
    item = Item(**args)
    db.session.add(item)
    db.session.commit()

    return jsonify(ItemSchema(many=True).dump(Item.query.all()))


@bp.get("/items/<int:id>")
def get_single_item(id: int) -> Item:
    item = Item.query.filter(Item.id == id).first_or_404()
    return jsonify(ItemSchema().dump(item))


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

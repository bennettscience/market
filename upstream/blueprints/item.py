from typing import List

from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from htmx_flask import make_response, request
from webargs import fields
from webargs.flaskparser import parser

from upstream.charts import ChartService
from upstream.extensions import db, htmx
from upstream.models import Event, Item
from upstream.schemas import ItemSchema


bp = Blueprint("items", __name__)

@bp.get("/items")
@login_required
def get_items() -> List[Item]:
    template = 'items/index.html'
    items = Item.query.order_by(Item.name).all()

    resp_data = {
        "items": ItemSchema(many=True).dump(items)
    }

    if request.htmx:
        resp = render_template(template, items=items)
    else:
        resp = render_template('shared/layout-wrap.html', partial=template, data=resp_data)

    return resp

@bp.get("/items/create")
@login_required
def create_item_form():
    return make_response(
        render_template(
            "shared/partials/sidebar.html",
            partial="forms/create-item.html",
            push_url="/items/create",
        )
    )

@bp.post("/items")
@login_required
def post_item() -> List[Item]:
    args = parser.parse(ItemSchema(), location="form")
    item = Item(**args)
    db.session.add(item)
    db.session.commit()

    items = Item.query.order_by('name').all()

    return make_response(
        render_template("items/index.html", items=ItemSchema(many=True).dump(items)),
        trigger={"showToast": "Added item sucecssfully.", "clearInput": "true"},
    )

@bp.get("/items/<int:id>")
@login_required
def get_single_item(id: int) -> Item:
    from upstream.charts import ItemChartBuilder
    item = Item.query.filter(Item.id == id).first_or_404()

    template = "items/item-detail.html"
    
    if item.sales.all():
        builder = ItemChartBuilder(item)
        chart = builder.build()
    else:
        chart = 'No data.'

    resp_data = {
        "item": item,
        "chart": chart
    }

    if request.htmx:
        resp = render_template(template, **resp_data)
    else:
        resp = render_template("shared/layout-wrap.html", partial=template, data=resp_data)

    return resp


@bp.delete("/events/<int:id>")
@login_required
def delete_single_item(id: int) -> List[Item]:
    item = Item.query.filter(Item.id == id).first_or_404()
    db.session.delete(item)
    db.session.commit()

    return jsonfiy(ItemSchema(many=True).dump(Item.query.all()))

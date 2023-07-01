from typing import List

from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from htmx_flask import make_response, request
from webargs import fields
from webargs.flaskparser import parser

from upstream.charts import ChartService
from upstream.extensions import db, htmx
from upstream.models import Event, Item, ItemType
from upstream.schemas import ItemSchema
from upstream.utils import object_to_select
from upstream.wrappers import templated

bp = Blueprint("items", __name__)

@bp.route("/items", methods=["GET"])
@templated(template='items/index.html')
@login_required
def get_items() -> List[Item]:
    template = 'items/index.html'
    items = Item.query.order_by(Item.name).all()

    resp_data = {
        "items": ItemSchema(many=True).dump(items)
    }

    # if request.htmx:
    #     resp = render_template(template, items=items)
    # else:
    #     resp = render_template('shared/layout-wrap.html', partial=template, data=resp_data)

    return resp_data

@bp.get("/items/create")
@login_required
def create_item_form():
    types = object_to_select(ItemType.query.all())

    content = {
        "options": types
    }

    return make_response(
        render_template(
            "shared/partials/sidebar.html",
            partial="forms/create-item.html",
            push_url="/items/create",
            data=content
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

@bp.get("/items/<int:id>/edit")
@login_required
def get_item_form(id: int) -> Item:
    item = Item.query.filter(Item.id == id).first_or_404()
    template = "forms/edit-item.html"

    types = object_to_select(ItemType.query.all())

    resp_data = {
        "item": item,
        "options": types,
        "selected": item.itemtype_id
    }

    return render_template("shared/partials/sidebar.html", partial=template, data=resp_data)


@bp.put("/items/<int:id>")
@login_required
def edit_item(id: int) -> Item:
    args = parser.parse({
        "name": fields.Str(),
        "itemtype_id": fields.Int(),
        "abbreviation": fields.Str()
    }, location="form")

    item = Item.query.filter(Item.id == id).first_or_404()

    item.update(args)

    # Update the item list
    items = Item.query.order_by(Item.name).all()

    return make_response(
        render_template("items/index.html", items=ItemSchema(many=True).dump(items)),
        trigger={"showToast": "Updated item sucecssfully.", "clearInput": "true"},
    )


@bp.get("/items/<int:id>/delete")
@login_required
def get_delete_confirm(id: int):
    item = Item.query.filter(Item.id == id).first_or_404()

    return render_template(
        "shared/partials/sidebar.html",
        partial="forms/delete-item.html",
        data=item
    )

@bp.delete("/items/<int:id>")
@login_required
def delete_single_item(id: int) -> List[Item]:
    item = Item.query.filter(Item.id == id).first_or_404()
    db.session.delete(item)
    db.session.commit()

    items = Item.query.order_by(Item.name).all()

    return make_response(
        render_template("items/index.html", items=ItemSchema(many=True).dump(items)),
        trigger={"showToast": "Item and all records deleted."}
    )

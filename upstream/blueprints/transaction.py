from pprint import pprint

from flask import Blueprint, jsonify, render_template
from htmx_flask import make_response
from webargs import fields
from webargs.flaskparser import parser

from upstream.charts import EventChartBuilder, ChartService
from upstream.extensions import db, htmx
from upstream.models import Event, Item, Transaction
from upstream.schemas import EventSchema, TransactionSchema


bp = Blueprint("transactions", __name__)


@bp.get("/sales")
def get_all_sales():
    sales = Transaction.query.order_by(Transaction.occurred_at).all()
    gross = Transaction().gross_sales()
    return render_template(
        "sales/index.html", sales=TransactionSchema(many=True).dump(sales), gross=gross
    )


@bp.get("/sales/<int:event_id>")
def get_sale_form(event_id):
    args = parser.parse({"item_id": fields.Int()}, location="querystring")
    item = Item.query.filter(Item.id == args["item_id"]).first()
    data = {"event_id": event_id, "item": item}
    return render_template(
        "sales/partials/sale-form.html",
        data=data,
    )


@bp.post("/sales/<int:event_id>")
def make_sale(event_id):

    args = parser.parse(
        {
            "event_item_id": fields.Int(),
            "quantity": fields.Int(),
            "price_per_item": fields.Float(),
        },
        location="form",
    )

    event = Event.query.filter(Event.id == event_id).first()

    sale = Transaction(
        event_id=event_id,
        event_item_id=args["event_item_id"],
        price_per_item=args["price_per_item"],
        quantity=args["quantity"],
    )
    db.session.add(sale)
    db.session.commit()

    sales = event.gross_sales()

    data = EventChartBuilder(event).build()
    chart = ChartService(data).stacked_bar()

    template = render_template(
        "events/partials/event-table.html", event=event, sales=sales, chart=chart
    )

    return make_response(
        template,
        trigger={"showToast": "Sale added!", "saleComplete": True},
    )

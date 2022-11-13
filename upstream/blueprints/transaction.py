from flask import Blueprint, jsonify, render_template
from htmx_flask import make_response
from webargs import fields
from webargs.flaskparser import parser

from upstream.extensions import db, htmx
from upstream.models import Transaction
from upstream.schemas import TransactionSchema


bp = Blueprint("transactions", __name__)


@bp.get("/sales")
def get_all_sales():
    sales = Transaction.query.order_by(Transaction.occurred_at).all()
    return render_template(
        "sales/index.html", sales=TransactionSchema(many=True).dump(sales)
    )

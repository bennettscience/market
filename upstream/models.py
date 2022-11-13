from sqlalchemy.dialects.mysql import FLOAT
from sqlalchemy.sql import func
from upstream.extensions import db


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    sales = db.relationship("Transaction", backref="item", lazy="dynamic")
    events = db.relationship("EventItem", backref="item", lazy="dynamic")

    def gross_sales(self):
        return sum([(sale.price_per_item * sale.quantity) for sale in self.sales])


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    address = db.Column(db.String(250))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


# One to many
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    starts = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    sales = db.relationship(
        "Transaction", backref="event", lazy="dynamic", uselist=True
    )
    inventory = db.relationship(
        "EventItem", backref="event", uselist=True, lazy="dynamic"
    )

    def gross_sale(self):
        return sum([(sale.price_per_item * sale.quantity) for sale in self.sales])


class EventItem(db.Model):
    __tablename__ = "event_item"
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("event.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    item_id = db.Column(
        db.Integer, db.ForeignKey("item.id", onupdate="CASCADE"), primary_key=True
    )
    quantity = db.Column(db.Integer)


class Transaction(db.Model):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    occurred_at = db.Column(db.DateTime(timezone=True), default=func.now())
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("event.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    event_item_id = db.Column(db.Integer, db.ForeignKey("item.id", onupdate="CASCADE"))
    price_per_item = db.Column(FLOAT(precision=20, scale=10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

from sqlalchemy.dialects.mysql import FLOAT
from upstream.extensions import db


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    sales = db.relationship("Transaction", backref="sale", uselist=True)
    event_inventory = db.relationship("EventItem", backref="item")


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
    created_at = db.Column(db.DateTime)

    sales = db.relationship("Transaction", backref="event", uselist=True)

    inventory = db.relationship("EventItem", backref="event", uselist=True)


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
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("event.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    event_item_id = db.Column(
        db.Integer, db.ForeignKey("item.id", onupdate="CASCADE"), primary_key=True
    )
    price_per_item = db.Column(FLOAT(precision=20, scale=10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

from flask_login import UserMixin
from sqlalchemy.dialects.mysql import FLOAT
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

from upstream.extensions import db, login_manager

class Manager(object):
    def update(self, data):

        for key, value in data.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        pass


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    abbreviation = db.Column(db.String(32), nullable=True)
    itemtype_id = db.Column(db.Integer, db.ForeignKey("item_type.id"))

    sales = db.relationship("Transaction", backref="item", lazy="dynamic")
    events = db.relationship("EventItem", backref="item", lazy="dynamic")

    def gross_sales(self):
        return sum([(sale.price_per_item * sale.quantity) for sale in self.sales])


class ItemType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    address = db.Column(db.String(250))


class Market(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(32), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



# One to many
class Event(Manager, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    market_id = db.Column(db.Integer, db.ForeignKey("market.id"), nullable=False)
    starts = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    note = db.Column(db.String(1500))

    market = db.relationship("Market", backref="event", uselist=False)

    sales = db.relationship(
        "Transaction", backref="event", lazy="dynamic", uselist=True
    )
    inventory = db.relationship(
        "EventItem", backref="event", uselist=True, lazy="dynamic"
    )

    def gross_sales(self):
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

    @hybrid_property
    def available(self):
        sale_records = self.event.sales.filter(
            Transaction.event_item_id == self.item.id
        ).all()
        sold = [sale.quantity for sale in sale_records]
        sales = sum(sold)

        if sales >= self.quantity:
            return 0
        else:
            return self.quantity - sales

    @hybrid_property
    def sold(self):
        sale_records = self.event.sales.filter(
            Transaction.event_item_id == self.item.id
        ).all()
        return sum([sale.quantity for sale in sale_records])


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

    @classmethod
    def gross_sales(self):
        sales = self.query.all()
        totals = [(sale.quantity * sale.price_per_item) for sale in sales]
        return sum(totals)

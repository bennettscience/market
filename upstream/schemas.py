from marshmallow import Schema, fields


class EventItemSchema(Schema):
    item = fields.Nested("ItemSchema")
    quantity = fields.Int()
    available = fields.Int()


class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    market = fields.Nested("MarketSchema")
    starts = fields.DateTime(format="%m/%d/%y %I:%M %p")
    note = fields.String()

    inventory = fields.Nested("EventItemSchema", many=True)
    sales = fields.Nested("TransactionSchema", many=True)


class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    itemtype_id = fields.Int()
    abbreviation = fields.String()


class MarketSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()


class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    item = fields.Nested("ItemSchema")
    event = fields.Nested(
        "EventSchema",
        exclude=(
            "sales",
            "inventory",
        ),
    )
    price_per_item = fields.Float()
    quantity = fields.Int()
    occurred_at = fields.DateTime()

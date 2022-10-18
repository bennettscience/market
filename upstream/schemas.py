from marshmallow import Schema, fields


class EventItemSchema(Schema):
    item = fields.Nested("ItemSchema")
    quantity = fields.String()


class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    starts = fields.DateTime()

    inventory = fields.Nested(EventItemSchema, many=True)


class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()

from marshmallow import Schema, fields


class PetSchema(Schema):
    id = fields.Integer(required=False)
    name = fields.Str(required=True)
    tag = fields.Str(required=False)

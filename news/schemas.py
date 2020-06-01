from marshmallow import Schema
from marshmallow import fields


class MediumSchema(Schema):
    title = fields.String(dump_only=True)
    uri = fields.String(dump_only=True)
    slant = fields.String(dump_only=True)


class ArticleSchema(Schema):
    uri = fields.String(dump_only=True)
    url = fields.String(dump_only=True)
    title = fields.String(dump_only=True)
    content = fields.String(dump_only=True)
    image = fields.String(dump_only=True)
    datetime = fields.DateTime(dump_only=True)


class EventSchema(Schema):
    uri = fields.String(dump_only=True)
    title = fields.String(dump_only=True)
    summary = fields.String(dump_only=True)
    date = fields.DateTime(dump_only=True)
    articles = fields.Nested(ArticleSchema, many=True)

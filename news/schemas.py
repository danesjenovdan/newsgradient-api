from marshmallow import Schema
from marshmallow import fields
from marshmallow import validate

from constants import Orientations
from constants import TimeRange


class MediumSchema(Schema):
    title = fields.String(dump_only=True)
    uri = fields.String(dump_only=True)
    slant = fields.String(dump_only=True)
    favicon = fields.String(dump_only=True)


class ArticleSchema(Schema):
    uri = fields.String(dump_only=True, data_key='id')
    url = fields.String(dump_only=True)
    title = fields.String(dump_only=True)
    content = fields.String(dump_only=True)
    image = fields.String(dump_only=True)
    datetime = fields.DateTime(dump_only=True)
    medium = fields.Nested(MediumSchema)


class EventArticlesSchema(Schema):
    articles = fields.Nested(ArticleSchema, many=True)
    title = fields.String(dump_only=True)


class EventSchema(Schema):
    uri = fields.String(dump_only=True, data_key='id')
    title = fields.String(dump_only=True)
    summary = fields.String(dump_only=True)
    image = fields.String(dump_only=True)
    date = fields.DateTime(dump_only=True)
    first_publish = fields.String(dump_only=True, data_key='firstPublish')
    articles = fields.Nested(ArticleSchema, many=True)
    articles_count = fields.Int(dump_only=True, data_key='articleCount')
    all_articles_count = fields.Int(dump_only=True, data_key='allArticlesCount')


class TopEventQPSchema(Schema):
    # timerange = fields.String(default=TimeRange.LAST_MONTH,
    #                           load_only=True,
    #                           required=False,
    #                           validate=validate.OneOf([t.value for t in TimeRange]))
    slant = fields.Int(default=Orientations.NEUTRAL,
                       load_only=True,
                       required=False,
                       validate=validate.OneOf([t.value for t in Orientations]))

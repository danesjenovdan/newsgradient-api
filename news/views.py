import typing
from datetime import datetime
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count
from django.db.models import F
from django.db.models import FloatField
from django.db.models import Q
from django.db.models.functions import Cast
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from common.views import SuperAPIView
from constants import CacheKeys
from constants import TimeRange
from constants import Orientations
from news import models
from news import serializers
from news.schemas import EventArticlesSchema
from news.schemas import EventSchema
from news.schemas import TopEventQPSchema
from news.services import get_event
from news.services import get_event_articles
from news.services import get_most_popular_events_with_articles


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventSerializer
    queryset = models.Event.objects.all()
    filter_fields = ('is_visible',)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super(EventViewSet, self).get_permissions()

    def get_queryset(self):
        time_range = self.request.GET.get('range', 'all')
        slant = self.request.GET.get('slant', 'all')

        # get all events and annotate field count of articles per event
        events = models.Event.objects.all().annotate(
            all_count=Cast(
                Count(
                    'articles',
                    filter=Q(articles__medium__slant__isnull=False),
                    distinct=True
                ),
                FloatField()
            )
        )

        if time_range == TimeRange.TODAY:
            events = events.filter(date=datetime.today())
        if time_range == TimeRange.YESTERDAY:
            events = events.filter(date=datetime.today() - timedelta(days=1))
        if time_range == TimeRange.LAST_WEEK:
            events = events.filter(date__gte=datetime.today() - timedelta(days=7))
        if time_range == TimeRange.LAST_MONTH:
            events = events.filter(date__gte=datetime.today() - timedelta(days=30))
        else:
            events = events.all()

        if slant == 'all':
            return events.exclude(articles__isnull=True).annotate(
                this_count=Cast(
                    Count(
                        'articles'
                    ),
                    FloatField()
                )
            ).order_by('-all_count')
        else:
            events = events.filter(articles__medium__slant=slant)
            # annotate field count of articles of this slant per event and returns orderd queryset
            return events.annotate(
                this_count=Cast(
                    Count(
                        'articles',
                        filter=Q(articles__medium__slant=slant),
                        distinct=True
                    ),
                    FloatField()
                )
            ).annotate(ordering=F('this_count') / F('all_count')).order_by('-ordering')


class ArticleView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, event_id):
        cache_key = f'{CacheKeys.EVENT_ARTICLES}::{event_id}'
        cached_value = cache.get(cache_key)
        if not cached_value:
            service_response: typing.List[typing.Dict] = get_event_articles(event_id)
            schema = EventArticlesSchema()
            data = schema.dump(service_response)
            cache.set(cache_key, data)
            return Response(data)
        return Response(cached_value)


class TopEventsView(SuperAPIView):
    permission_classes = (AllowAny,)
    qp_schema = TopEventQPSchema

    def get(self, request):
        # time_range = self.cleaned_qp.get('timerange')
        slant = self.cleaned_qp.get('slant')
        if slant is None:
            slant = Orientations.NEUTRAL.value

        cache_key = f'{CacheKeys.TOP_EVENTS}::{slant}'
        cached_value = cache.get(cache_key)
        if not cached_value:
            events: typing.List[typing.Dict] = get_most_popular_events_with_articles(slant)
            schema = EventSchema(many=True)
            data = schema.dump(events)
            cache.set(cache_key, data)
            return Response(data)
        return Response(cached_value)

        # events: typing.List[typing.Dict] = get_most_popular_events_with_articles(slant)
        # schema = EventSchema(many=True)
        # data = schema.dump(events)
        # return Response(data)


class EventDetailView(APIView):
    permission_classes = (AllowAny,)
    qp_schema = TopEventQPSchema

    def get(self, request, event_id):
        event: typing.Dict = get_event(event_id)
        schema = EventSchema()
        data = schema.dump(event)
        return Response(data)

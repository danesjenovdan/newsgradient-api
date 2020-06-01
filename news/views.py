import typing
from datetime import datetime
from datetime import timedelta

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

from constants import TimeRange
from news import models
from news import serializers
# Create your views here.
from news.schemas import EventSchema
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

        if self.request.query_params.get('popular') is not None and self.action == 'list':
            return get_most_popular_events()

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


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ArticleSerializer
    queryset = models.Article.objects.all().prefetch_related('medium')
    filter_fields = ('event',)


class TopEventsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        events: typing.List[typing.Dict] = get_most_popular_events_with_articles()
        schema = EventSchema(many=True)
        return Response(schema.dump(events))

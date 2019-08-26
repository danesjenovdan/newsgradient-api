from django.db.models import Count, Q, F, FloatField
from django.db.models.functions import Cast

from rest_framework import viewsets, mixins, permissions

from news import serializers, models

from datetime import datetime, timedelta

# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventSerializer
    queryset = models.Event.objects.all()
    filter_fields = ('is_visible',)

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

        if time_range == 'today':
            events = events.filter(date=datetime.today())
        if time_range == 'yesterday':
            events = events.filter(date=datetime.today()-timedelta(days=1))
        if time_range == 'last-week':
            events = events.filter(date__gte=datetime.today()-timedelta(days=7))
        if time_range == 'last-month':
            events = events.filter(date__gte=datetime.today()-timedelta(days=30))
        else:
            events = events.all()

        if slant == 'all':
            return  events.exclude(articles__isnull=True).annotate(
                this_count=Cast(
                    Count(
                        'articles'
                    ),
                    FloatField()
                )
            ).order_by('-all_count')
        else:
            print('slant order')
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
            ).annotate(ordering=F('this_count')/F('all_count')).order_by('-ordering')


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ArticleSerializer
    queryset = models.Article.objects.all().prefetch_related('medium')
    filter_fields = ('event',)
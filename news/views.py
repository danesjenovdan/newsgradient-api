from django.db.models import Count, Q, F

from rest_framework import viewsets, mixins, permissions

from news import serializers, models

from datetime import datetime, timedelta

# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventSerializer
    queryset = models.Event.objects.all()

    def get_queryset(self):
        time_range = self.request.GET.get('range', 'today')
        slant = self.request.GET.get('slant', 'all')

        events = models.Event.objects.all().annotate(
            all_count=Count(
                'articles',
                filter=Q(articles__medium__slant__isnull=False),
                distinct=True
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
            return  events.annotate(
                this_count=Count(
                    'articles'
                )
            ).order_by('-all_count')
        else:
            print('slant order')
            events = events.filter(articles__medium__slant=slant).distinct()

            # added fields for all articles count and count for articles this slant
            return events.annotate(
                this_count=Count(
                    'articles',
                    filter=Q(articles__medium__slant=slant),
                    distinct=True
                )
            ).order_by(F('this_count')/F('all_count'))



class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ArticleSerializer
    queryset = models.Article.objects.all().prefetch_related('medium')
    filter_fields = ('event',)
from django.db.models import Count, Q

from news.models import Event


def get_most_popular_events():
    events = Event.objects.prefetch_related('articles').all().annotate(
        articles_count=Count('articles'),
    ).order_by('-articles_count')[:5]
    return events

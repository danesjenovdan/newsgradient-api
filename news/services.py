from datetime import datetime
from datetime import timedelta

from django.db.models import Count
from rest_framework.exceptions import NotFound

from constants import Orientations
from constants import TimeRange
from news.models import Article
from news.models import Event
from news.models import Medium


def get_most_popular_events_with_articles(time_range=None, slant=Orientations.NEUTRAL):
    mediums = {medium.get('id'): medium for medium in Medium.objects.all().values()}

    promoted_events = Event.objects \
        .select_related('articles') \
        .annotate(all_articles_count=Count('articles')) \
        .values('uri', 'title', 'summary', 'date', 'all_articles_count') \
        .filter(is_promoted=True) \
        .order_by('-all_articles_count')
    promoted_events_count = len(promoted_events)

    events = []
    if promoted_events_count < 5:
        events = Event.objects.all()
        if time_range == TimeRange.TODAY.value:
            events = events.filter(date=datetime.today())
        elif time_range == TimeRange.YESTERDAY.value:
            events = events.filter(date=datetime.today() - timedelta(days=1))
        elif time_range == TimeRange.LAST_WEEK.value:
            events = events.filter(date__gte=datetime.today() - timedelta(days=7))
        elif time_range == TimeRange.LAST_MONTH.value:
            events = events.filter(date__gte=datetime.today() - timedelta(days=30))
        events = events.select_related('articles') \
                     .annotate(all_articles_count=Count('articles')) \
                     .values('uri', 'title', 'summary', 'date', 'all_articles_count') \
                     .order_by('-all_articles_count')[:5 - promoted_events_count]
    elif promoted_events_count > 5:
        promoted_events = promoted_events[:5]

    final_events = list(promoted_events) + list(events)
    for event in final_events:
        articles = Article.objects.select_related('medium') \
                       .filter(event_id=event.get('uri'), medium__slant=slant) \
                       .values('uri', 'url', 'title', 'content', 'image', 'datetime', 'medium_id')[:3]

        for article in articles:
            article['medium'] = mediums.get(article.get('medium_id'))
        event['articles'] = articles

    return final_events


def get_event_articles(event_uri):
    try:
        event = Event.objects.values('title').get(uri=event_uri)
    except Event.DoesNotExist:
        raise NotFound
    mediums = {medium.get('id'): medium for medium in Medium.objects.all().values()}
    articles = Article.objects.select_related('medium').filter(event_id=event_uri).values()
    for article in articles:
        article['medium'] = mediums.get(article.get('medium_id'))

    data = {
        'title': event.get('title'),
        'articles': list(articles)
    }
    return data


def get_event(event_uri):
    try:
        return Event.objects.defer('updated_at', 'is_promoted', 'sentimment', 'wgt') \
            .values() \
            .get(uri=event_uri)
    except Event.DoesNotExist:
        raise NotFound

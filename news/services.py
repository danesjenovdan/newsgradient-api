from datetime import datetime

from django.db.models import Count
from django.db.models import Q
from rest_framework.exceptions import NotFound

from constants import Orientations
from news.models import Article
from news.models import Event
from news.models import Medium


def get_most_popular_events_with_articles(slant: int = Orientations.NEUTRAL):
    mediums = {medium.get('id'): medium for medium in Medium.objects.all().values()}

    promoted_events = Event.objects \
        .select_related('articles') \
        .annotate(all_articles_count=Count('articles')) \
        .values('uri', 'title', 'summary', 'date', 'all_articles_count') \
        .filter(is_promoted=True) \
        .order_by('-all_articles_count')

    final_events = list(promoted_events)
    for event in final_events:
        articles = Article.objects.select_related('medium') \
                       .filter(event_id=event.get('uri'), medium__slant=slant) \
                       .order_by('-medium__reliability') \
            .values('uri', 'url', 'title', 'content', 'image', 'datetime', 'medium_id')
        for article in articles:
            article['medium'] = mediums.get(article.get('medium_id'))
            event['image'] = article.get('image') if article.get('image') else None
        event['articles'] = articles[:3]
        event['all_articles_count'] = articles.count()
        if len(articles):
            d = datetime.utcnow() - articles[0].get('datetime').replace(tzinfo=None)
            hours = int(d.total_seconds() // 3600)
            if hours <= 24:
                event['first_publish'] = f'{hours} hours ago'
            elif 24 < hours <= 48:
                event['first_publish'] = f'yesterday'
            elif hours > 48:
                event['first_publish'] = f'More than 2 days ago'

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
        return Event.objects.defer('updated_at', 'is_promoted', 'sentiment', 'wgt') \
            .values() \
            .get(uri=event_uri)
    except Event.DoesNotExist:
        raise NotFound


def determine_slant_from_bias(bias: float) -> Orientations:
    if bias <= -4:
        return Orientations.LEFT
    elif -4 <= bias <= 4:
        return Orientations.NEUTRAL
    else:
        return Orientations.RIGHT

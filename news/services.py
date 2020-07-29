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
        event['articles_count'] = articles.count()
        if len(articles):
            d = datetime.utcnow() - articles[0].get('datetime').replace(tzinfo=None)
            hours = int(d.total_seconds() // 3600)
            if hours <= 1:
                event['first_publish'] = f'Prije sat vremena'
            elif 1 < hours <= 2:
                event['first_publish'] = f'Prije dva sata'
            elif 2 < hours <= 3:
                event['first_publish'] = f'Prije tri sata'
            elif 3 < hours <= 5:
                event['first_publish'] = f'Prije pet sati'
            elif 5 < hours <= 24:
                event['first_publish'] = f'Danas'
            elif 24 < hours <= 48:
                event['first_publish'] = f'Jučer'
            elif 48 < hours <= 72:
                event['first_publish'] = f'Prije dva dana'
            elif 72 < hours <= 96:
                event['first_publish'] = f'Prije tri dana'
            elif 96 < hours <= 120:
                event['first_publish'] = f'Prije četiri dana'
            elif 120 < hours <= 144:
                event['first_publish'] = f'Prije pet dana'
            elif hours > 144:
                event['first_publish'] = f'Prije više od pet dana'

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
    if bias < -3:
        return Orientations.LEFT
    if bias > 3:
        return Orientations.RIGHT
    return Orientations.NEUTRAL

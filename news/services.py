
from news.models import Article
from news.models import Event


def get_most_popular_events_with_articles():
    events = Event.objects.all() \
     .order_by('-article_count') \
     .values('uri', 'title', 'summary', 'date')[:5]
    print(events.query)
    for event in events:
        articles = Article.objects.filter(event_id=event.get('uri'))\
            .values('uri', 'url', 'title', 'content', 'image', 'datetime')[:5]
        event['articles'] = articles
        print(event.get('uri'), event.get('article_count'), len(articles))
    return events

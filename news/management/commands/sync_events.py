import datetime
import os

from django.core.management import BaseCommand
from eventregistry import EventRegistry
from eventregistry import QueryEventArticlesIter
from eventregistry import QueryEventsIter
from eventregistry import QueryItems
from eventregistry import RequestEventsInfo

import constants
from news.models import Article
from news.models import Event
from news.models import Medium


class Command(BaseCommand):
    def handle(self, *args, **options):
        key = os.getenv('ER_API_KEY')
        locationUris = [
            'http://en.wikipedia.org/wiki/Bosnia_and_Herzegovina',
            'http://en.wikipedia.org/wiki/Croatia',
            'http://en.wikipedia.org/wiki/Serbia_and_montenegro',
        ]
        mediums_dict = Command.get_mediums()

        er = EventRegistry(apiKey=key)

        q = QueryEventsIter(locationUri=QueryItems.OR(locationUris),
                            dateStart=datetime.datetime.now() - datetime.timedelta(days=7),
                            lang=QueryItems.OR(['hrv', 'srp']))
        q.setRequestedResult(RequestEventsInfo(sortBy='size'))

        self.stdout.write('Started fetching Events')
        events = er.execQuery(q)
        self.stdout.write('Finished fetching Events')
        for event in events.get('events').get('results'):
            uri = event.get('uri')
            title = event.get('title').get(constants.Languages.CROATIAN, '') or event.get('title') \
                .get(constants.Languages.SERBIAN, '')
            summary = event.get('summary').get(constants.Languages.CROATIAN, '') or event.get('summary') \
                .get(constants.Languages.SERBIAN, '')
            event_date = event.get('eventDate')
            article_count = event.get('totalArticleCount')
            sentiment = event.get('sentiment')
            wgt = event.get('wgt')

            existing_event = Event.objects.filter(uri=uri).first()
            if existing_event:
                existing_event.article_count = article_count
                existing_event.save(update_fields=['article_count'])
            else:
                new_event = Event()
                new_event.title = title
                new_event.summary = summary
                new_event.article_count = article_count
                new_event.wgt = wgt
                new_event.sentiment = sentiment
                new_event.date = datetime.datetime.strptime(event_date, '%Y-%m-%d')
                new_event.uri = uri
                new_event.save()
                self.stdout.write(f'Created event with uri {new_event.uri}')

        date_filter = datetime.datetime.utcnow() - datetime.timedelta(days=14)
        top_five_events = Event.objects.filter(date__gte=date_filter).order_by('-article_count')[:5]
        self.stdout.write(f'Top five events are: {top_five_events}')
        for event in top_five_events:
            self.stdout.write(f'Started fetching articles for event {event.uri}')
            Command.handle_articles(er, event.uri, mediums_dict)
            self.stdout.write(f'Finished fetching articles for event {event.uri}')
            self.stdout.write('\n-----------------------------\n')

    @staticmethod
    def handle_articles(er, event_uri, mediums):
        iter = QueryEventArticlesIter(event_uri, lang=QueryItems.OR(['hrv', 'srp']))
        results = iter.execQuery(er)
        for article in results:
            uri = article.get('uri')
            url = article.get('url')
            title = article.get('title')
            content = article.get('body')
            datetime = article.get('dateTime')
            image = article.get('image')
            sentiment = article.get('sentiment')
            # medium_url = article.get('source', {}).get('uri', '')

            existing_article = Article.objects.filter(uri=uri).first()
            if not existing_article:
                Article.objects.create(
                    uri=uri,
                    title=title,
                    content=content,
                    url=url,
                    datetime=datetime,
                    image=image,
                    event_id=event_uri,
                    sentiment=sentiment,
                    medium_id=mediums.get('test.ba')
                    # medium=mediums.get(medium_url)
                )

    @staticmethod
    def get_mediums():
        mediums = Medium.objects.all()
        return {medium.uri: medium.id for medium in mediums}

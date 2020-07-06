import datetime
import os

import favicon
import requests
from django.core.cache import cache
from django.core.management import BaseCommand
from django.core.management import call_command
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
        if cache.get(constants.EVENT_FETCH_KEY) == constants.CommandStatus.RUNNING.value:
            return
        try:
            cache.set(constants.EVENT_FETCH_KEY, constants.CommandStatus.RUNNING.value)
            self.handle_events()
            call_command('clear_cache')
        except Exception:
            pass
        cache.set(constants.EVENT_FETCH_KEY, constants.CommandStatus.RUNNING.IDLE)

    def handle_events(self):
        key = os.getenv('ER_API_KEY')
        # location_uris = [
        #     'http://en.wikipedia.org/wiki/Bosnia_and_Herzegovina',
        #     'http://en.wikipedia.org/wiki/Croatia',
        #     'http://en.wikipedia.org/wiki/Serbia_and_montenegro',
        # ]
        mediums_dict = Command.get_mediums()

        er = EventRegistry(apiKey=key)

        q = QueryEventsIter(
            dateStart=datetime.datetime.now() - datetime.timedelta(days=7),
            lang=QueryItems.OR(['hrv', 'srp'])
        )
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
            images = event.get('images', [])

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
                if len(images):
                    new_event.images = images[0]
                new_event.save()
                self.stdout.write(f'Created event with uri {new_event.uri}')

        date_filter = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        events = Event.objects.filter(date__gte=date_filter).order_by('-article_count')
        self.stdout.write(f'Top five events are: {events}')
        for event in events:
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
            image = article.get('image', '')
            if not image:
                image = ''
            image = image.replace('http://', 'https://')
            sentiment = article.get('sentiment')
            medium_url = article.get('source', {}).get('uri', '')

            existing_article = Article.objects.filter(uri=uri).first()
            medium_id = mediums.get(medium_url, None)
            if not existing_article and medium_id is not None:
                Article.objects.create(
                    uri=uri,
                    title=title,
                    content=content,
                    url=url,
                    datetime=datetime,
                    image=image,
                    event_id=event_uri,
                    sentiment=sentiment,
                    medium_id=medium_id
                )

    @staticmethod
    def get_mediums():
        mediums = Medium.objects.all()
        return {medium.uri: medium.id for medium in mediums}

    @staticmethod
    def get_medium_favicons():
        for medium in Medium.objects.filter(favicon=None):
            print(medium.title)
            try:
                icons = favicon.get('http://' + medium.uri)
            except Exception:
                pass
            png_icons = list(filter(lambda x: x.format == 'png', icons))
            ico_icons = list(filter(lambda x: x.format == 'ico', icons))
            ss_png_icons = list(filter(lambda x: x.width == x.height and x.width > 0, png_icons))
            found = False
            for img in ss_png_icons:
                try:
                    if requests.get(img.url).status_code == 200:
                        medium.favicon = img.url
                        medium.save()
                        found = True
                except:
                    pass
                if found:
                    break
            if not found and ico_icons:
                print(ico_icons)
                ico_response = requests.get(ico_icons[0].url)
                if ico_response.status_code == 200:
                    medium.favicon = ico_response.url
                    medium.save()

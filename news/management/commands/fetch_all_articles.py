import datetime
import os

import favicon
import requests
from django.core.cache import cache
from django.core.management import BaseCommand
from django.core.management import call_command
from eventregistry import EventRegistry
from eventregistry import QueryArticlesIter
from eventregistry import QueryItems

import constants
from news.models import Article
from news.models import Medium


class Command(BaseCommand):
    def handle(self, *args, **options):
        if cache.get(constants.ALL_ARTICLES_FETCH) == constants.CommandStatus.RUNNING.value:
            return
        try:
            cache.set(constants.ALL_ARTICLES_FETCH, constants.CommandStatus.RUNNING.value)
            self.handle_events()
            call_command('clear_cache')
        except Exception:
            pass
        cache.set(constants.ALL_ARTICLES_FETCH, constants.CommandStatus.RUNNING.IDLE)

    def handle_events(self):
        key = os.getenv('ER_API_KEY')
        location_uris = [
            'http://en.wikipedia.org/wiki/Bosnia_and_Herzegovina',
            'http://en.wikipedia.org/wiki/Croatia',
            'http://en.wikipedia.org/wiki/Serbia_and_montenegro',
        ]
        mediums = Command.get_mediums()

        er = EventRegistry(apiKey=key)

        q = QueryArticlesIter(
            dateStart=datetime.datetime.now() - datetime.timedelta(days=7),
            lang=QueryItems.OR(['hrv', 'srp'])
        )
        self.stdout.write('Started fetching Articles')
        articles = q.execQuery(er)
        self.stdout.write('Finished fetching Articles')
        for article in articles:
            uri = article.get('uri')
            url = article.get('url')
            title = article.get('title')
            content = article.get('body')
            dt = article.get('dateTime')
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
                    datetime=dt,
                    image=image,
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

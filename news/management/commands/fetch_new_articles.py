from django.core.cache import cache
from django.core.management import BaseCommand, call_command
from eventregistry import *

import constants
from news.models import Article
from news.models import Event
from news.models import Medium

import datetime
import os
import traceback
import favicon
import requests
from pprint import pprint


def get_medium_uris():
    mediums = Medium.objects.all()
    return [medium.uri for medium in mediums]
    # return {medium.uri: medium.id for medium in mediums}


class Command(BaseCommand):
    def handle(self, *args, **options):
        if cache.get(constants.NEW_ARTICLES_FETCH_KEY) == constants.CommandStatus.RUNNING.value:
            self.stderr.write('Command already running!')
            return
        try:
            cache.set(constants.NEW_ARTICLES_FETCH_KEY, constants.CommandStatus.RUNNING.value)
            self.handle_impl()
            call_command('update_event_uris')
            call_command('clear_cache')
        except Exception as e:
            self.stderr.write(f'Exception: {e}')
            traceback.print_exc()
        cache.set(constants.NEW_ARTICLES_FETCH_KEY, constants.CommandStatus.IDLE.value)

    def handle_impl(self):
        key = os.getenv('ER_API_KEY')
        er = EventRegistry(apiKey=key)
        self.stdout.write('-' * 80)

        medium_uris = get_medium_uris()
        self.stdout.write(f'Medium URIs: {medium_uris}')
        self.stdout.write('-' * 80)

        q = QueryArticlesIter(
            sourceUri=QueryItems.OR(medium_uris),
            lang=QueryItems.OR(['hrv', 'srp']),
            dateStart=datetime.datetime.now() - datetime.timedelta(days=7),
            isDuplicateFilter='skipDuplicates',
        )
        all_articles_count = q.count(er)
        self.stdout.write(f'Got articles: {all_articles_count}')
        self.stdout.write('-' * 80)

        results = q.execQuery(
            er,
            # maxItems=10,
        )

        newEventsCount = 0
        newArticlesCount = 0

        count = 0
        for article in results:
            count += 1
            self.stdout.write(f'{count} / {all_articles_count}')

            articleUrl = article.get('url', '')
            if 'index.hr/oglasi' in articleUrl:
                continue

            articleUri = article.get('uri', '')
            if Article.objects.filter(uri=articleUri).exists():
                continue

            mediumUri = article.get('source', {}).get('uri')
            medium = Medium.objects.filter(uri=mediumUri).first()
            if not medium:
                continue

            eventUri = article.get('eventUri', '')
            # some fields have max length so truncate to prevent db errors
            articleUrl = articleUrl[:512]
            articleTitle = (article.get('title', '') or '')[:512]
            articleImage = (article.get('image', '') or '')[:512]
            articleBody = article.get('body', '')
            articleDateTime = article.get('dateTime')

            # self.stdout.write(f'articleTitle = {articleTitle}')
            # self.stdout.write(f'articleUrl   = {articleUrl}')
            # self.stdout.write(f'eventUri     = {eventUri}')

            if eventUri and not Event.objects.filter(uri=eventUri).exists():
                q = QueryEvent(eventUri)
                q.setRequestedResult(RequestEventInfo())
                res = er.execQuery(q)

                while True:
                    newEventUri = res.get(eventUri, {}).get('newEventUri')
                    if not newEventUri:
                        break
                    self.stdout.write(f'newEventUri: {newEventUri} from {eventUri}')
                    eventUri = newEventUri
                    q = QueryEvent(eventUri)
                    q.setRequestedResult(RequestEventInfo())
                    res = er.execQuery(q)

                if not Event.objects.filter(uri=eventUri).exists():
                    eventInfo = res.get(eventUri, {}).get('info')
                    if not eventInfo:
                        pprint(res)

                    eventTitle = (eventInfo.get('title').get('hrv', '') or eventInfo.get('title').get('srp', '') or '')[:512]
                    eventSummary = eventInfo.get('summary').get('hrv', '') or eventInfo.get('summary').get('srp', '') or ''
                    eventDate = datetime.datetime.strptime(eventInfo.get('eventDate'), '%Y-%m-%d')

                    Event.objects.create(
                        uri=eventUri,
                        title=eventTitle,
                        summary=eventSummary,
                        article_count=0,
                        date=eventDate,
                    )
                    self.stdout.write(f'NEW EVENT: {eventUri} - {eventTitle}')
                    newEventsCount += 1

            Article.objects.create(
                uri=articleUri,
                title=articleTitle,
                content=articleBody,
                url=articleUrl,
                datetime=articleDateTime,
                image=articleImage,
                event_id=eventUri,
                medium=medium,
            )
            self.stdout.write(f'NEW ARTICLE: {articleUri} - {articleTitle}')
            newArticlesCount += 1

            self.stdout.write('-' * 80)

        self.stdout.write('-' * 80)
        self.stdout.write(f'+ new events:   {newEventsCount}')
        self.stdout.write(f'+ new articles: {newArticlesCount}')
        self.stdout.write('-' * 80)
        self.stdout.write('+ DONE')
        self.stdout.write('-' * 80)

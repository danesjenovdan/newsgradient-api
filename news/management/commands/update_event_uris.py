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


class Command(BaseCommand):
    def handle(self, *args, **options):
        if cache.get(constants.UPDATE_EVENT_URIS_KEY) == constants.CommandStatus.RUNNING.value:
            self.stderr.write('Command already running!')
            return
        try:
            cache.set(constants.UPDATE_EVENT_URIS_KEY, constants.CommandStatus.RUNNING.value)
            self.handle_impl()
            call_command('clear_cache')
        except Exception as e:
            self.stderr.write(f'Exception: {e}')
            traceback.print_exc()
        cache.set(constants.UPDATE_EVENT_URIS_KEY, constants.CommandStatus.IDLE.value)

    def handle_impl(self):
        key = os.getenv('ER_API_KEY')
        er = EventRegistry(apiKey=key)
        self.stdout.write('-' * 80)

        all_events = Event.objects.all()
        all_events_count = all_events.count()
        self.stdout.write(f'All events: {all_events_count}')
        self.stdout.write('-' * 80)

        all_event_uris = list(all_events.values_list('uri', flat=True))
        segment_size = 50
        segmented_event_uris = [all_event_uris[ev:ev+segment_size] for ev in range(0, all_events_count, segment_size)]
        segment_count = len(segmented_event_uris)

        allRes = {}
        count = 0
        for segment in segmented_event_uris:
            count += 1
            self.stdout.write(f'{count} / {segment_count}')
            q = QueryEvent(segment)
            q.setRequestedResult(RequestEventInfo())
            res = er.execQuery(q)
            allRes.update(res)

        newEventsCount = 0
        updatedArticlesCount = 0

        count = 0
        for event in all_events:
            count += 1
            self.stdout.write(f'{count} / {all_events_count}')
            event_articles = event.articles.all()
            if not event_articles.exists():
                continue

            eventUri = event.uri
            res = allRes

            while True:
                newEventUri = res.get(eventUri, {}).get('newEventUri')
                if not newEventUri:
                    break
                self.stdout.write(f'newEventUri: {newEventUri} from {eventUri}')
                eventUri = newEventUri
                q = QueryEvent(eventUri)
                q.setRequestedResult(RequestEventInfo())
                res = er.execQuery(q)

            if event.uri == eventUri:
                continue

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

            updatedArticlesCount += event_articles.update(event_id=eventUri)
            self.stdout.write('-' * 80)

        self.stdout.write('-' * 80)
        self.stdout.write(f'+ new events:       {newEventsCount}')
        self.stdout.write(f'+ updated articles: {newEventsCount}')
        self.stdout.write('-' * 80)
        self.stdout.write('+ DONE')
        self.stdout.write('-' * 80)

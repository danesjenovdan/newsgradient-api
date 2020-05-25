from datetime import datetime, timedelta

import favicon
import metadata_parser
import requests
from django.conf import settings
from eventregistry import *

from news import models


class Refresher(object):
    def __init__(self):
        self.er = EventRegistry(apiKey=settings.ER_API_KEY)
        self.events = list(models.Event.objects.values_list('uri', flat=True))
        self.articles = list(models.Article.objects.values_list('uri', flat=True))

    def start(self):
        self.refresh_data()
        self.set_semtiment()
        self.get_favicons()
        self.get_og_tags()

    def refresh_data(self):
        q = QueryEvents(
            categoryUri=self.er.getCategoryUri("politics"),
            dateStart=(datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
            dateEnd=datetime.today().strftime("%Y-%m-%d"),
            sourceLocationUri=self.er.getLocationUri("USA"),
            conceptUri=self.er.getConceptUri("USA"))
        page = 1
        pages = 100
        while page <= pages:
            q.setRequestedResult(RequestEventsInfo(page=page, count=50,
                                                   returnInfo=ReturnInfo(
                                                       articleInfo=ArticleInfoFlags(concepts=True, categories=True,
                                                                                    image=True))))
            page += 1

            res = self.er.execQuery(q)
            pages = res['events']['pages']
            responses = []
            for i in res['events']['results']:
                responses.append(self.add_event(i))
            print(responses.count(True), ' added events')
            print('On page: ', page, ' of ', pages)

        q = QueryArticles(
            categoryUri=self.er.getCategoryUri("politics"),
            dateStart=(datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
            dateEnd=datetime.today().strftime("%Y-%m-%d"),
            sourceLocationUri=self.er.getLocationUri("USA"),
            conceptUri=self.er.getConceptUri("USA"))
        page = 1
        pages = 100
        while page <= pages:
            q.setRequestedResult(RequestArticlesInfo(page=page, count=100,
                                                     returnInfo=ReturnInfo(
                                                         articleInfo=ArticleInfoFlags(concepts=True, categories=True,
                                                                                      image=True))))
            page += 1
            res = self.er.execQuery(q)
            pages = res['articles']['pages']
            responses = []
            for i in res['articles']['results']:
                responses.append(self.add_article(i))
            print(responses.count(True), ' added articles')
            print('On page: ', page, ' of ', pages)

    def get_or_add_medium(self, data):
        medium = models.Medium.objects.filter(uri=data['source']['uri'])
        if not medium:
            medium = models.Medium(
                title=data['source']['title'],
                uri=data['source']['uri']
            )
            medium.save()
            return medium
        else:
            return medium[0]

    def add_event(self, data):
        if data['uri'] not in self.events:
            if 'eng' not in data['title'].keys() and 'eng' not in data['summary'].keys():
                return
            event = models.Event(
                title=data['title']['eng'],
                summary=data['summary']['eng'],
                date=datetime.strptime(data['eventDate'], '%Y-%m-%d').date(),
                uri=data['uri'],
            )
            if 'images' in data.keys():
                event.images = data['images']
            event.save()
            self.events.append(data['uri'])
            return True
        else:
            return False

    def add_article(self, data):
        if data['uri'] in self.articles:
            return False
        else:
            if not data['eventUri']:
                return False
            medium = self.get_or_add_medium(data)
            try:
                event = models.Event.objects.get(uri=data['eventUri'])
            except:
                # print('event doesnt exist')
                return False
            if 'eng' != data['lang']:
                return

            models.Article(
                medium=medium,
                event=event,
                title=data['title'],  # ['eng'],
                image=data['image'],
                content=data['body'],
                uri=data['uri'],
                datetime=datetime.strptime(data['dateTime'], '%Y-%m-%dT%H:%M:%SZ'),
                url=data['url'],
                sentiment=data['sentiment']
            ).save()
            self.articles.append(data['uri'])
            return True

    def set_semtiment(self):
        analytics = Analytics(self.er)
        print("Articles: ", models.Article.objects.all().count())
        print("Articles without sentiment: ", models.Article.objects.filter(sentiment=None).count())
        for article in models.Article.objects.filter(sentimentRNN=None):
            if not article.sentiment:
                cat = analytics.sentiment(article.content)
                article.sentiment = cat['avgSent']

            catRNN = analytics.sentiment(article.content, method='rnn')
            article.sentimentRNN = catRNN['avgSent']

            article.save()

    def get_favicons(self):
        for medium in models.Medium.objects.filter(favicon=None):
            print(medium.title)
            try:
                icons = favicon.get('http://' + medium.uri)
            except:
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

    def get_og_tags(self):
        articles = models.Article.objects.filter(og_title=None)
        all = articles.count()
        i = 0
        for article in articles:
            print(article.url)
            i += 1
            try:
                page = metadata_parser.MetadataParser(url=article.url)
            except:
                continue
            article.og_title = get_first_or_none(page.get_metadatas('title', strategy=['og', ]))
            article.og_description = get_first_or_none(page.get_metadatas('description', strategy=['og', ]))
            article.og_image = get_first_or_none(page.get_metadatas('image', strategy=['og', ]))
            article.save()
            print(i, 'of', all)


def get_first_or_none(item):
    return item[0] if item else None

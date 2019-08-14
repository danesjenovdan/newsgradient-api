from django.conf import settings

from eventregistry import *

from news import models

from datetime import datetime


class Refresher(object):
    def __init__(self):
        self.er = EventRegistry(apiKey=settings.ER_API_KEY)
        self.events = list(models.Event.objects.values_list('uri', flat=True))
        self.articles = list(models.Article.objects.values_list('uri', flat=True))
        self.refresh_data()

    def refresh_data(self):
        q=QueryEvents(
            categoryUri=self.er.getCategoryUri("politics"),
            dateStart="2019-08-12",
            dateEnd="2019-08-14",
            sourceLocationUri=self.er.getLocationUri("USA"),
            conceptUri=self.er.getConceptUri("USA"))
        page = 1
        pages = 100
        while page <= pages:
            q.setRequestedResult(RequestEventsInfo(page = page, count = 50,
                returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True, categories = True, image = True))))
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
            dateStart="2019-08-12",
            dateEnd="2019-08-14",
            sourceLocationUri=self.er.getLocationUri("USA"),
            conceptUri=self.er.getConceptUri("USA"))
        page = 1
        pages = 100
        while page <= pages:
            q.setRequestedResult(RequestArticlesInfo(page = page, count = 100,
                returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True, categories = True, image = True))))
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
                event.images=data['images']
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
                #print('event doesnt exist')
                return False
            #if 'eng' not in data['title'].keys():
            #    return

            models.Article(
                medium=medium,
                event=event,
                title=data['title'],#['eng'],
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
        for article in Article.object.filter(sentiment=None):
            cat = analytics.sentiment(article.content)

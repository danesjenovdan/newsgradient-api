from threading import Thread

import favicon
import requests
from django.core.management import BaseCommand

from news.models import Medium


class Command(BaseCommand):
    def handle(self, *args, **options):
        thread_list = []
        for medium in Medium.objects.filter(favicon=None):
            print(medium.title)
            t = Thread(target=Command.get_favicon, args=(medium,))
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()

    @staticmethod
    def get_favicon(medium: Medium):
        try:
            icons = favicon.get('http://' + medium.uri)
        except Exception:
            return
        if not icons:
            return
        png_icons = list(filter(lambda x: x.format == 'png', icons))
        ico_icons = list(filter(lambda x: x.format == 'ico', icons))
        ss_png_icons = list(filter(lambda x: x.width == x.height and x.width > 0, png_icons))
        found = False
        for img in ss_png_icons:
            try:
                if requests.get(img.url).status_code == 200:
                    medium.favicon = img.url.replace('http://', 'https://')
                    medium.save()
                    found = True
            except:
                pass
            if found:
                return
        if not found and ico_icons:
            print(ico_icons)
            ico_response = requests.get(ico_icons[0].url)
            if ico_response.status_code == 200:
                medium.favicon = ico_response.url.replace('http://', 'https://')
                medium.save()

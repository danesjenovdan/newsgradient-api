from django.core.management import BaseCommand

from news.models import Medium


class Command(BaseCommand):
    def handle(self, *args, **options):
        input_data = input()
        rows = input_data.split(';')
        print(rows)
        for row in rows:
            data = row.split(',')
            uri = data[0]
            title = data[1]
            # bias = data[2]
            # reliability = data[3]
            # count = data[4]

            existing_medium = Medium.objects.filter(uri=uri).first()
            if not existing_medium:
                Medium.objects.create(
                    title=title,
                    uri=uri,
                )

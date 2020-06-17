import csv

from news.models import Medium
from news.services import determine_slant_from_bias


def update_mediums(csv_text):
    csv_text = csv_text.replace('\r', '')

    for row in csv_text.split('\n'):
        data = row.split(',')
        uri = data[0][1:]
        bias = float(data[1])
        # bias = data[2]
        reliability = float(data[2])
        # count = data[4]

        existing_medium: Medium = Medium.objects.filter(uri=uri).first()
        if not existing_medium:
            Medium.objects.create(
                title='Test medium',
                uri=uri,
                slant=determine_slant_from_bias(bias).value,
                reliability=reliability
            )
        else:
            existing_medium.slant = determine_slant_from_bias(bias).value
            existing_medium.reliability = reliability
            existing_medium.save()

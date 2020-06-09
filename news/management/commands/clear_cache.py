from django.core.cache import cache
from django.core.management import BaseCommand

from constants import CacheKeys
from constants import Orientations
from constants import TimeRange


class Command(BaseCommand):
    def handle(self, *args, **options):
        keys = []
        for time_range in TimeRange:
            for slant in Orientations:
                key = f'{CacheKeys.TOP_EVENTS}::{time_range.value}::{slant.value}'
                keys.append(key)

        cache.delete_many(keys)

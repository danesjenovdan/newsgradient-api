from enum import Enum


class TimeRange(Enum):
    TODAY = 'today'
    YESTERDAY = 'yesterday'
    LAST_WEEK = 'last-week'
    LAST_MONTH = 'last-month'


class Orientations(Enum):
    LEFT = 1
    NEUTRAL = 2
    RIGHT = 3


class Reliability(Enum):
    FACT_REPORTING = 'fact_reporting'
    OPINION_PERSUASION = 'opinion_persuasion'
    PROPAGANDA = 'propaganda'


class Languages:
    CROATIAN = 'hrv'
    SERBIAN = 'srp'


class CacheKeys:
    EVENTS = 'events'
    TOP_EVENTS = 'top_events'
    EVENT_ARTICLES = 'event-articles'


UPDATE_EVENT_URIS_KEY = 'update_event_uris_key'
NEW_ARTICLES_FETCH_KEY = 'new_articles_fetch_key'
EVENT_FETCH_KEY = 'sync_events_command'
ALL_ARTICLES_FETCH = 'all_articles_fetch'


class CommandStatus(Enum):
    IDLE = '0'
    RUNNING = '1'

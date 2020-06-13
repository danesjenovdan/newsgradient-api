from enum import Enum


class TimeRange(Enum):
    TODAY = 'today'
    YESTERDAY = 'yesterday'
    LAST_WEEK = 'last-week'
    LAST_MONTH = 'last-month'


class Orientations(Enum):
    FAR_LEFT = 1
    LIBERAL = 2
    NEUTRAL = 3
    CONSERVATIVE = 4
    FAR_RIGHT = 5


class Languages:
    CROATIAN = 'hrv'
    SERBIAN = 'srp'


class CacheKeys:
    EVENTS = 'events'
    TOP_EVENTS = 'top_events'
    EVENT_ARTICLES = 'event-articles'


EVENT_FETCH_KEY = 'sync_events_command'


class CommandStatus(Enum):
    IDLE = '0'
    RUNNING = '1'

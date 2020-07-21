from django.contrib import admin
from django.db.models import Count
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models.functions import Cast

from constants import Orientations
from news import models


# Register your models here.

class MediumAdmin(admin.ModelAdmin):
    list_display = ['title', 'uri', 'slant', 'favicon']
    search_fields = ['title', 'uri']
    list_filter = ['slant']
    list_editable = ('slant',)


class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'number_of_articles', 'is_promoted', 'left_count', 'neutral_count', 'right_count']
    search_fields = ['title', 'summary']
    list_filter = ['date', 'is_promoted']
    list_editable = ('is_promoted',)

    def get_queryset(self, request):
        return models.Event.objects.prefetch_related('articles').all().annotate(
            _all_count=Cast(
                Count(
                    'articles',
                    filter=Q(articles__medium__slant__isnull=False),
                    distinct=True
                ),
                IntegerField()
            ),
            _left_count=Cast(
                Count(
                    'articles',
                    filter=Q(articles__medium__slant=Orientations.LEFT.value),
                    distinct=True
                ),
                IntegerField()
            ),
            _neutral_count=Cast(
                Count(
                    'articles',
                    filter=Q(articles__medium__slant=Orientations.NEUTRAL.value),
                    distinct=True
                ),
                IntegerField()
            ),
            _right_count=Cast(
                Count(
                    'articles',
                    filter=Q(articles__medium__slant=Orientations.RIGHT.value),
                    distinct=True
                ),
                IntegerField()
            )
        )

    def number_of_articles(self, obj):
        return obj._all_count

    def left_count(self, obj):
        return obj._left_count

    def neutral_count(self, obj):
        return obj._neutral_count

    def right_count(self, obj):
        return obj._right_count

    number_of_articles.admin_order_field = '_all_count'
    left_count.admin_order_field = '_left_count'
    neutral_count.admin_order_field = '_neutral_count'
    right_count.admin_order_field = '_right_count'


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'medium']
    search_fields = ['title', 'content']
    list_filter = ['event', 'medium']
    list_select_related = ('medium',)
    autocomplete_fields = ['event']


admin.site.register(models.Medium, MediumAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Article, ArticleAdmin)

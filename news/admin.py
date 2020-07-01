from django.contrib import admin
from django.db.models import Count
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models.functions import Cast

from news import models


# Register your models here.

class MediumAdmin(admin.ModelAdmin):
    list_display = ['title', 'uri', 'slant']
    search_fields = ['title', 'uri']
    list_filter = ['slant']
    list_editable = ('slant',)


class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'number_of_articles', 'article_count', 'is_promoted']
    search_fields = ['title', 'summary']
    list_filter = ['date', 'is_promoted']
    list_editable = ('is_promoted',)

    def get_queryset(self, request):
        return models.Event.objects.all().annotate(
            all_count=Cast(
                Count(
                    'articles',
                    filter=Q(articles__medium__slant__isnull=False),
                    distinct=True
                ),
                IntegerField()
            )
        )

    def number_of_articles(self, obj):
        return obj.all_count


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'medium']
    list_filter = ['event', 'medium']
    list_select_related = ('medium',)


admin.site.register(models.Medium, MediumAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Article, ArticleAdmin)

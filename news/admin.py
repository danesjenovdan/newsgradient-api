from django.contrib import admin
from news import models
# Register your models here.

class MediumAdmin(admin.ModelAdmin):
    list_display = ['title', 'uri', 'slant']
    search_fields = ['title', 'uri']
    list_filter = ['slant']
    list_editable = ('slant',)


class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'get_articles_count', 'is_hidden']
    search_fields = ['title', 'summary']
    list_filter = ['date', 'is_hidden']
    list_editable = ('is_hidden',)

    def get_articles_count(self, obj):
        return obj.articles.count()

admin.site.register(models.Medium, MediumAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Article)
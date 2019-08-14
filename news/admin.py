from django.contrib import admin
from news import models
# Register your models here.

class MediumAdmin(admin.ModelAdmin):
    list_display = ['title', 'uri', 'slant']
    search_fields = ['title', 'uri']
    list_filter = ['slant']
    list_editable = ('slant',)

admin.site.register(models.Medium, MediumAdmin)
admin.site.register(models.Event)
admin.site.register(models.Article)
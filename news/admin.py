from django.contrib import admin
from news import models
# Register your models here.

admin.site.register(models.Medium)
admin.site.register(models.Event)
admin.site.register(models.Article)
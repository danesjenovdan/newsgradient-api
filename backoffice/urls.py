from django.urls import path

from backoffice.views import ClearCacheView

urlpatterns = [
    path('clear-cache/', ClearCacheView.as_view(), name='backoffice.clear_cache')
]
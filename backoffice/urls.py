from django.urls import path

from backoffice.views import BackofficeView

urlpatterns = [
    path('', BackofficeView.as_view(), name='backoffice.clear_cache')
]
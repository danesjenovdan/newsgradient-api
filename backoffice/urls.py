from django.urls import path

from backoffice.views import BackofficeView
from backoffice.views import BackofficeMediumView

urlpatterns = [
    path('', BackofficeView.as_view(), name='backoffice'),
    path('mediums/', BackofficeMediumView.as_view(), name='backoffice.mediums')
]
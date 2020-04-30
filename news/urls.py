from django.conf.urls import include, url
from django.urls import path

from rest_framework.routers import DefaultRouter

from news import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'articles', views.ArticleViewSet)

urlpatterns = [
    url('^', include(router.urls)),
]

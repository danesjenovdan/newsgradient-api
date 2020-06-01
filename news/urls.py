from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from news import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'articles', views.ArticleViewSet)

urlpatterns = [
    url('^', include(router.urls)),
    url('top-events/', views.TopEventsView.as_view()),
]

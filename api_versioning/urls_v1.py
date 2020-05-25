from django.conf.urls import url
from django.urls import include

urlpatterns = [
    url('news/', include('news.urls'))
]
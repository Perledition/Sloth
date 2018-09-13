

from django.conf.urls import url, include
from .views import Database, DatabaseList

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', Database.as_view(), name='todo-rud'),
    url(r'^$', DatabaseList.as_view(), name='todo-List'),
]
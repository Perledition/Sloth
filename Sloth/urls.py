
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from .router import router
from . import viewsset
from rest_framework.authtoken import views


""" Das muss noch angepasst werden! Das Goto ist wichtiger Bestandteile der Redirection. Funktioniert aber in dieser API konstellation nicht. Alternativ statt view.py viewset.py nennen """
urlpatterns = [
    url(r'^$', viewsset.goto, name='sloth'),
    url(r'^sloth/', include('todo.urls', namespace='todo')),
    url(r'^user-api-interface/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api-token-auth/', views.obtain_auth_token, name='api-token-auth'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

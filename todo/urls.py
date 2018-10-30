from django.conf.urls import url, include
from django.urls import path
from . import views
# from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete



app_name='todo'

urlpatterns = [
    #todo urls
    url(r'^todo/$', views.Dashboard.as_view(), name='index'),
    url(r'^add/$', views.addTodo, name='add'),
    url(r'^(?P<todo_id>[0-9]+)/delete/$', views.deleteTodo, name='delete'),
    url(r'^(?P<todo_id>[0-9]+)/$', views.TodoDetail.as_view(), name='detail'),
    url(r'^(?P<todo_id>[0-9]+)/complete/$', views.completeTodo, name='complete'),
    url(r'^(?P<todo_id>[0-9]+)/additem/$', views.addItem, name='addItem'),
    url(r'^(?P<todo_id>[0-9]+)/chatitem/$', views.addmsg, name='addmsg'),
    url(r'^(?P<Item_id>[0-9]+)/checkItem/$', views.checkItem, name='checkItem'),


    # trophy urls
    url(r'^(?P<project_id>[0-9]+)/trophy/$', views.DetailTrophy.as_view(), name='pro'),
    url(r'^(?P<project_id>[0-9]+)/trophy-delete/$', views.delete_Trophy, name='trophy-delete'),
    url(r'^(?P<project_id>[0-9]+)/trophy-done/$', views.done_Trophy, name='trophy-done'),
    url(r'^trophy/add/create/$', views.createProject, name='create'),
    url(r'^trophy/$', views.TrophyIndex, name='trophy'),

    # Statistik
    url(r'^stats/$', views.Stats.as_view(), name='stats'),

    # Learn
    url(r'^todo/learn_it$', views.Learn.as_view(), name='learn'),
    url(r'^todo/hard_like/$', views.like, name='hard_like'),
    url(r'^todo/hard_dislike/$', views.dislike, name='hard_dislike'),

    # User urls
    url(r'^register/$', views.Registration.as_view(), name='register'),
    url(r'^$', views.LoginUser.as_view(), name='login'),
    url(r'^logout_user/$', views.logout_user, name='logout'),
    url(r'^account/$', views.UserAccount.as_view(), name='account'),
    url(r'^account/delete$', views.delete_user, name='account_delete'),
    url(r'^sloth/delete_info$', views.delete_info, name='delete_info'),
    url(r'^account/change_Password/$', views.ChangePassword.as_view(), name='change_password'),

    # email zum Passwort ändern! Funktioniert nur mit Mailprovider
    #url(r'^reset-password/$', password_reset, name='reset_password'),
    #url(r'^reset-password/done/$', password_reset_done, name='password_reset_done'),
    #url(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name='password_reset_confirm'),
    #url(r'^reset-password/complete/$', password_reset_complete, name='password_reset_complete'),

    # contact
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^contact/info/$', views.info, name='contact_info'),
    url(r'^Feedback/$', views.Feedback.as_view(), name='feedback'),
    url(r'^Feedback/info$', views.feedback_info, name='feedback_info'),
    url(r'^NewbieFeedback/$', views.FirstFeedback.as_view(), name='first_feedback'),
    url(r'^Datenschutz/$', views.datenschutz, name='datenschutz'),
    url(r'^Nutzung/$', views.Nutzung, name='Nutzung'),

    # 404 response
    url(r'^PageNotFound/$', views.error404, name='404'),
]

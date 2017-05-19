from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'', views.PlayerListView.as_view()),
    url(r'^game/(?P<pk>\d+)/$', views.GameDetailView.as_view()),
]
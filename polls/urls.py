
from django.urls import path

from . import views
from polls import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('polls/message/', views.IndexView.handle_message, name='handle_message'),
]


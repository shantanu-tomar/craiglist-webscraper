from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('new_search/', views.new_search, name = 'new_search'),
    path('new_search/post_detail/', views.post_detail, name = 'post_detail'),
    url(r'^share/mail/$', views.share_by_mail, name='share_by_mail'),
    ]
    
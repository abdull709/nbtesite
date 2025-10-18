from django.urls import path
from . import views

app_name = 'nbtelog'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about_us, name='about'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('search/', views.search, name='search'),
    path('servicom/', views.servicom, name='servicom'),
    path('departments/aprs-ict/', views.aprs_ict, name='aprs_ict'),
    path('departments/nbte-coex/', views.nbtecoex, name='nbtecoex'),
    path('tvet-institutions/', views.tvet_institutions, name='tvet_institutions'),
    path('odfel/', views.odfel, name='odfel'),
    path('odfel/guidelines/', views.odfel_guidelines, name='odfel_guidelines'),
    path('nsq-benefits/', views.nsq_benefits, name='nsq_benefits'),
    path('nsq/', views.nsq, name='nsq'),
    path('nsqf/', views.nsqf, name='nsqf'),
    path('nsqf/levels/', views.nsqf_levels, name='nsqf_levels'),
    path('research-development/', views.research_development, name='research_development'),
    path('downloads/', views.downloads, name='downloads'),
    path('chat/', views.chat, name='chat'),
]
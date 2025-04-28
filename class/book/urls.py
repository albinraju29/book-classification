from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('processing/', views.processing, name='processing'),
    path('predict/', views.predict, name='predict'), 
    path('result/', views.result, name='result'),
    path('error/', views.error, name='error'),
]
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('processing/', views.processing, name='processing'),
    path('results/', views.result, name='result'), 
    path('error/', views.error, name='error'),
    path('recent-predictions/', views.recent_predictions, name='recent_predictions'),
    path('prediction/<int:prediction_id>/', views.prediction_detail, name='prediction_detail'),
]
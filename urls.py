from django.urls import path
from . import views

app_name = "calendarapp"

urlpatterns = [
    path('authorize/', views.google_authorize, name='authorize'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('create_event/', views.create_event_view, name='create_event'),
    path('oauth_success/', views.oauth_success, name='oauth_success'),
]
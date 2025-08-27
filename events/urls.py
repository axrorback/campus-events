from django.urls import path
from . import views

app_name = 'events'
urlpatterns = [
    path('', views.public_list, name='public_list'),
    path('event/<int:pk>/', views.event_detail, name='detail'),
    path('event/<int:pk>/register/', views.register_event, name='register'),
    path('my/', views.my_events, name='my_events'),
    path('create/', views.create_event, name="create"),  # 🔥 qo‘shildi

]

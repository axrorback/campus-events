from django.urls import path
from .views import login_view, logout_view, profile_view
app_name = "users"   # 🔑 bu namespace uchun kerak

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path("profile/", profile_view, name="profile"),

]

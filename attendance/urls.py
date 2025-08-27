from django.urls import path
from . import views

app_name = 'attendance'
urlpatterns = [
    path('scan/', views.scan_page, name='scan_page'),               # admin/volunteer sahifa
    path('resolve/<uuid:reg_id>/', views.resolve_registration, name='resolve'),  # QR payload targeti
    path('mark/<uuid:reg_id>/', views.mark_attended, name='mark'),  # qatnashdi deb belgilash
    path('report/', views.report, name='report'),                    # filtr bilan hisobot
    path("check_qr/", views.check_qr, name="check_qr"),
    path("logs/", views.attendance_logs, name="attendance_logs"),
    path("clear_logs/", views.clear_logs, name="clear_logs"),
    path("clear_attendance/", views.clear_attendance, name="clear_attendance"),
    path("attended_list/", views.attended_list, name="attended_list"),

]

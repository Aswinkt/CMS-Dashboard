from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register-user/', views.user_registration, name='user_registration'),
    path('create-complaint/', views.complaint_create, name='complaint_create'),
    path('complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('complaint/<int:complaint_id>/edit/', views.complaint_edit, name='complaint_edit'),
    path('update-complaint-status/', views.update_complaint_status, name='update_complaint_status'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('debug/location/', views.debug_location, name='debug_location'),
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('checkin-status/', views.get_checkin_status, name='get_checkin_status'),
    path('checkin-history/', views.checkin_history, name='checkin_history'),
] 
from django.urls import path
from . import views
from . import views_debug
from django.contrib.auth import views as auth_views

app_name = 'notes'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('upload/', views.upload_study_material, name='upload_study_material'),
    path('materials/', views.study_material_list, name='study_material_list'),
    path('materials/download/<int:pk>/', views.download_study_material, name='download_study_material'),
    path('autocomplete/', views.autocomplete_suggestions, name='autocomplete_suggestions'),
    path('materials/<int:study_material_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('debug/users/', views_debug.list_users_profiles, name='debug_users'),
]


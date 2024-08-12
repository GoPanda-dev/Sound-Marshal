from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Example view
    path('select-role/', views.select_role, name='select_role'),
    path('create-artist-profile/', views.create_artist_profile, name='create_artist_profile'),
    path('create-curator-label-profile/', views.create_curator_label_profile, name='create_curator_label_profile'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('dashboard/artist/', views.artist_dashboard, name='artist_dashboard'),
    path('dashboard/curator/', views.curator_dashboard, name='curator_dashboard'),
    path('submit-track/<int:track_id>/', views.submit_track, name='submit_track'),
]

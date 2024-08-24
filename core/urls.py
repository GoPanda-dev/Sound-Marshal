from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Example view
    path('select-role/', views.select_role, name='select_role'),
    path('create-artist-profile/', views.create_artist_profile, name='create_artist_profile'),
    path('create-curator-label-profile/', views.create_curator_label_profile, name='create_curator_label_profile'),
    path('create-fan-profile/', views.create_fan_profile, name='create_fan_profile'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('profile/<slug:slug>/', views.profile_detail, name='profile_detail'),
    path('dashboard/artist/', views.artist_dashboard, name='artist_dashboard'),
    path('dashboard/curator/', views.curator_dashboard, name='curator_dashboard'),
    path('submit-track/<int:track_id>/', views.submit_track, name='submit_track'),

    # New URLs for Campaigns, Wallet, and Feedback
    path('wallet/', views.wallet, name='wallet'),
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/create/', views.create_campaign, name='create_campaign'),
    path('campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:campaign_id>/submissions/', views.submission_list, name='submission_list'),
    path('submissions/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('campaigns/overview/', views.campaign_overview, name='campaign_overview'),

    path('purchase-credits/', views.purchase_credits, name='purchase_credits'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('manage-subscription/', views.manage_subscription, name='manage_subscription'),
    path('submission/<int:submission_id>/feedback/', views.provide_feedback, name='provide_feedback'),
    path('search/', views.search, name='search'),
    path('track/<int:track_id>/', views.track_detail, name='track_detail'),

    path('explore/', views.explore, name='explore'),
    path('like-track/', views.like_track, name='like_track'),
    path('check-if-liked/<int:track_id>/', views.check_if_liked, name='check_if_liked'),
    path('toggle-like-track/', views.toggle_like_track, name='toggle_like_track'),
    path('track/<int:track_id>/add_comment/', views.add_comment, name='add_comment'),

    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-complete/', views.payment_complete, name='payment_complete'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),
]

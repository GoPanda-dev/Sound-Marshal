from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransactionViewSet, PaymentViewSet, SubscriptionViewSet, 
    CreditViewSet, ProfileViewSet, TrackViewSet, 
    CommentViewSet, CampaignViewSet, SubmissionViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'credits', CreditViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'tracks', TrackViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'submissions', SubmissionViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    # Add any additional API-specific URLs here
]

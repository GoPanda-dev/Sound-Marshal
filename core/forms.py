from django import forms
from django.contrib.auth.models import User  # Make sure to import the User model
from .models import Profile, Track, Submission, Campaign

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['comments']

class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'genre', 'file']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['feedback', 'rating', 'voice_feedback', 'video_feedback']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'genre', 'social_media_link', 'role']

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'target_genre', 'curators_targeted', 'budget']

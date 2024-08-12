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
        fields = [
            'role', 'name', 'bio', 'genre',
            'facebook_link', 'youtube_link', 'whatsapp_link',
            'instagram_link', 'tiktok_link', 'wechat_link',
            'messenger_link', 'telegram_link', 'viber_link', 'snapchat_link'
        ]

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'target_genre', 'curators_targeted', 'budget']

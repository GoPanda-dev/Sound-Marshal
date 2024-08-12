from django import forms
from django.contrib.auth.models import User
from .models import Profile, Track, Submission

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
        fields = ['feedback']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'genre', 'social_media_link', 'role']

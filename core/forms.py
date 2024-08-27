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
        fields = ['title', 'genre', 'description', 'cover_image', 'file']

class FeedbackForm(forms.ModelForm):
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Provide your feedback here...'}),
        required=False
    )
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'placeholder': 'Rate out of 5'}),
        required=False
    )
    voice_feedback = forms.FileField(
        required=False
    )
    video_feedback = forms.FileField(
        required=False
    )

    class Meta:
        model = Submission
        fields = ['feedback', 'rating', 'voice_feedback', 'video_feedback']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    GENRE_CHOICES = [
        ('Pop', 'Pop'),
        ('Hip Hop', 'Hip Hop'),
        ('Rock', 'Rock'),
        ('Electronic', 'Electronic'),
        ('Classical', 'Classical'),
        ('Jazz', 'Jazz'),
        ('Country', 'Country'),
        ('Reggae', 'Reggae'),
        ('Blues', 'Blues'),
        ('Soul', 'Soul'),
        ('R&B', 'R&B'),
        ('Metal', 'Metal'),
        ('Folk', 'Folk'),
        ('Punk', 'Punk'),
        ('Disco', 'Disco'),
        ('Latin', 'Latin'),
    ]

    genre = forms.MultipleChoiceField(
        choices=GENRE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select your genres"
    )

    class Meta:
        model = Profile
        fields = [
            'name', 'bio', 'genre', 'slug', 'profile_image', 'cover_image',
            'facebook_link', 'youtube_link', 'whatsapp_link', 'instagram_link', 
            'tiktok_link', 'wechat_link', 'messenger_link', 'telegram_link', 
            'viber_link', 'snapchat_link',
            'spotify_link', 'apple_music_link', 'amazon_music_link', 
            'youtube_music_link', 'deezer_link', 'tidal_link', 
            'soundcloud_link', 'pandora_link', 'audiomack_link', 'napster_link'
        ]
    def clean_genre(self):
        genres = self.cleaned_data.get('genre')
        # Convert the list of selected genres to a comma-separated string
        return ', '.join(genres)

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if Profile.objects.filter(slug=slug).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This URL is already taken. Please choose another.')
        return slug

class CampaignForm(forms.ModelForm):
    curators_targeted = forms.ModelMultipleChoiceField(queryset=User.objects.filter(profile__role='curator'))
    tracks = forms.ModelMultipleChoiceField(queryset=Track.objects.all())

    class Meta:
        model = Campaign
        fields = ['title', 'description', 'target_genre', 'budget', 'curators_targeted', 'tracks']
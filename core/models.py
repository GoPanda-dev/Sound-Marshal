import os
import random
import string
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError

import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()  # Number of tokens
    description = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} of {self.amount} tokens on {self.date}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)  # e.g., 'Completed', 'Failed'
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - ${self.amount} - {self.status} on {self.date}'

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Subscription for {self.user.username}"

    def cancel(self):
        stripe.Subscription.delete(self.stripe_subscription_id)
        self.active = False
        self.save()

class Credit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.credits} credits for {self.user.username}"


class Profile(models.Model):
    ROLE_CHOICES = (
        ('artist', 'Artist'),
        ('curator', 'Curator/Label'),
        ('fan', 'Fan'),  # Added option to sign up as a Fan
    )

    ALLOWED_GENRES = [
        'Pop', 'Hip Hop', 'Rock', 'Electronic', 'Classical',
        'Jazz', 'Country', 'Reggae', 'Blues', 'Soul',
        'R&B', 'Metal', 'Folk', 'Punk', 'Disco', 'Latin'
    ]

    tokens = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=100, default='None')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    followers = models.ManyToManyField(User, related_name='following', blank=True, symmetrical=False)

    liked_tracks = models.ManyToManyField('Track', related_name='liked_by', blank=True)

    # Profile images
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)

    # Streaming Service Links
    spotify_link = models.URLField(max_length=200, blank=True, null=True)
    apple_music_link = models.URLField(max_length=200, blank=True, null=True)
    amazon_music_link = models.URLField(max_length=200, blank=True, null=True)
    youtube_music_link = models.URLField(max_length=200, blank=True, null=True)
    deezer_link = models.URLField(max_length=200, blank=True, null=True)
    tidal_link = models.URLField(max_length=200, blank=True, null=True)
    soundcloud_link = models.URLField(max_length=200, blank=True, null=True)
    pandora_link = models.URLField(max_length=200, blank=True, null=True)
    audiomack_link = models.URLField(max_length=200, blank=True, null=True)
    napster_link = models.URLField(max_length=200, blank=True, null=True)

    # Social Media Links
    facebook_link = models.URLField(max_length=200, blank=True, null=True)
    youtube_link = models.URLField(max_length=200, blank=True, null=True)
    whatsapp_link = models.URLField(max_length=200, blank=True, null=True)
    instagram_link = models.URLField(max_length=200, blank=True, null=True)
    tiktok_link = models.URLField(max_length=200, blank=True, null=True)
    wechat_link = models.URLField(max_length=200, blank=True, null=True)
    messenger_link = models.URLField(max_length=200, blank=True, null=True)
    telegram_link = models.URLField(max_length=200, blank=True, null=True)
    viber_link = models.URLField(max_length=200, blank=True, null=True)
    snapchat_link = models.URLField(max_length=200, blank=True, null=True)

    role_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.role}"
    
    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'slug': self.slug})

    @property
    def is_artist(self):
        return self.role == 'artist'

    @property
    def is_curator(self):
        return self.role == 'curator'

    @property
    def is_fan(self):
        return self.role == 'fan'  # Added property for Fan role
    
    def is_followed_by(self, user):
        return self.followers.filter(id=user.id).exists()

    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        # Number of profiles the user is following
        return Profile.objects.filter(followers=self.user).count()

    def get_following_profiles(self):
        # Return profiles that the user is following
        return Profile.objects.filter(followers=self.user)
    
    def add_follower(self, follower):
        if not self.is_followed_by(follower):
            self.followers.add(follower)
            self.create_follow_notification(follower)
            self.save()

    def remove_follower(self, follower):
        if self.is_followed_by(follower):
            self.followers.remove(follower)
            self.save()

    def create_follow_notification(self, follower):
        Notification.objects.create(
            user=self.user,  # The user being followed
            notification_type='follow',
            message=f"{follower.username} has started following you!",
            link=reverse('profile_detail', kwargs={'slug': follower.profile.slug})
        )

    def clean(self):
        # Validate that the genre list only contains allowed genres
        if self.genre:
            genre_list = [g.strip() for g in self.genre.split(',')]
            for genre in genre_list:
                if genre not in self.ALLOWED_GENRES:
                    raise ValidationError(f"Genre '{genre}' is not allowed.")

    def save(self, *args, **kwargs):
        if not self.slug:
            random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            self.slug = slugify(f"{self.user.username}-{random_string}")
        super(Profile, self).save(*args, **kwargs)

    
class Track(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # New field for track description
    cover_image = models.ImageField(upload_to='track_covers/', blank=True, null=True)  # New field for cover image
    file = models.FileField(upload_to='tracks/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.track.title}"

class Campaign(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_genre = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    curators_targeted = models.ManyToManyField(User, related_name='targeted_campaigns')
    tracks = models.ManyToManyField(Track, related_name='campaigns')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def create_submissions(self):
        curators = self.curators_targeted.all()
        tracks = self.tracks.all()

        for curator in curators:
            for track in tracks:
                Submission.objects.create(
                    track=track,
                    curator=curator,
                    campaign=self
                )
                # Deduct a token from the artist's profile
                self.artist.profile.tokens -= 1
                self.artist.profile.save()

                # Ensure that the artist does not have negative tokens
                if self.artist.profile.tokens < 0:
                    self.artist.profile.tokens = 0
                    self.artist.profile.save()
                    # You might want to raise an error or handle the situation if tokens run out
                    raise ValueError("Not enough tokens to create more submissions.")


class Submission(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    curator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='curator_submissions')
    feedback = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('reviewed', 'Reviewed')], default='pending')
    comments = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    voice_feedback = models.FileField(upload_to='voice_feedback/', blank=True, null=True)
    video_feedback = models.FileField(upload_to='video_feedback/', blank=True, null=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)

    def __str__(self):
        return f"{self.track.title} to {self.curator.username}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new submission
        super().save(*args, **kwargs)
        if is_new:
            self.notify_curator()

    def notify_curator(self):
        Notification.objects.create(
            user=self.curator,
            notification_type='submission',
            message=f"New submission: {self.track.title}",
            link=reverse('submission_detail', kwargs={'submission_id': self.pk})
        )
        subject = f"New Submission: {self.track.title}"
        html_message = render_to_string('emails/new_submission.html', {'submission': self})
        plain_message = strip_tags(html_message)
        from_email = 'no-reply@soundmarshal.com'
        to = self.curator.email
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

def match_curators(campaign):
    curators = User.objects.filter(profile__role='curator', profile__genre=campaign.target_genre)
    return curators

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('submission', 'Submission'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        # Add more notification types as needed
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.message}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

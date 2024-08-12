from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def match_curators(track):
    curators = User.objects.filter(profile__role='curator', profile__genre=track.genre)
    return curators

class Track(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    file = models.FileField(upload_to='tracks/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    curator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='curator_submissions')
    feedback = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('reviewed', 'Reviewed')], default='pending')
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.track.title} to {self.curator.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.notify_curator()

    def notify_curator(self):
        subject = f"New Submission: {self.track.title}"
        html_message = render_to_string('emails/new_submission.html', {'submission': self})
        plain_message = strip_tags(html_message)
        from_email = 'no-reply@soundmarshal.com'
        to = self.curator.email
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)

class Profile(models.Model):
    ROLE_CHOICES = (
        ('artist', 'Artist'),
        ('curator', 'Curator/Label'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=100, default='None')
    social_media_link = models.URLField(max_length=200, blank=True, null=True)
    role_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.role}"

    @property
    def is_artist(self):
        return self.role == 'artist'

    @property
    def is_curator(self):
        return self.role == 'curator'

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

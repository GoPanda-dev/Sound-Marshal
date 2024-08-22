from django.contrib import admin
from .models import Profile, Track, Campaign, Submission, Transaction, Payment, Subscription, Credit, Comment

class LikedTracksInline(admin.TabularInline):
    model = Profile.liked_tracks.through  # Manage the many-to-many relationship through the intermediary table
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'role', 'tokens', 'genre', 'slug', 'role_selected', 'get_followers_count')
    search_fields = ('user__username', 'name', 'genre', 'slug')
    list_filter = ('role', 'role_selected')
    readonly_fields = ('tokens',)
    filter_horizontal = ('followers',)  # Adds a filterable interface for the followers field
    fieldsets = (
        (None, {
            'fields': ('user', 'role', 'name', 'bio', 'genre', 'slug', 'role_selected')
        }),
        ('Profile Images', {
            'fields': ('profile_image', 'cover_image')
        }),
        ('Followers', {
            'fields': ('followers',)  # Makes the followers field editable
        }),
        ('Streaming Service Links', {
            'fields': ('spotify_link', 'apple_music_link', 'amazon_music_link', 'youtube_music_link', 
                       'deezer_link', 'tidal_link', 'soundcloud_link', 'pandora_link', 
                       'audiomack_link', 'napster_link')
        }),
        ('Social Media Links', {
            'fields': ('facebook_link', 'youtube_link', 'whatsapp_link', 'instagram_link', 
                       'tiktok_link', 'wechat_link', 'messenger_link', 'telegram_link', 
                       'viber_link', 'snapchat_link')
        }),
        ('Tokens', {
            'fields': ('tokens',)
        }),
    )
    inlines = [LikedTracksInline]

    def get_followers_count(self, obj):
        return obj.followers.count()
    get_followers_count.short_description = 'Followers Count'

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'description', 'upload_date')
    search_fields = ('title', 'artist__username', 'genre', 'description')
    list_filter = ('genre', 'upload_date')
    fieldsets = (
        (None, {
            'fields': ('artist', 'title', 'genre', 'description', 'file')
        }),
        ('Additional Info', {
            'fields': ('cover_image',)
        }),
    )

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'target_genre', 'budget', 'created_at')
    search_fields = ('title', 'artist__username', 'target_genre')
    list_filter = ('target_genre', 'created_at')
    filter_horizontal = ('curators_targeted', 'tracks')
    fieldsets = (
        (None, {
            'fields': ('artist', 'title', 'description', 'target_genre', 'budget')
        }),
        ('Curators & Tracks', {
            'fields': ('curators_targeted', 'tracks')
        }),
    )

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('track', 'curator', 'status', 'submission_date', 'campaign')
    search_fields = ('track__title', 'curator__username', 'status', 'campaign__title')
    list_filter = ('status', 'submission_date', 'rating')
    fieldsets = (
        (None, {
            'fields': ('track', 'curator', 'campaign')
        }),
        ('Feedback', {
            'fields': ('feedback', 'rating', 'comments', 'voice_feedback', 'video_feedback')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
    readonly_fields = ('submission_date',)  # Readonly field for submission date
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # Only send notification on creation
            obj.notify_curator()

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'description', 'date')
    search_fields = ('user__username', 'transaction_type', 'description')
    list_filter = ('transaction_type', 'date')
    readonly_fields = ('date',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'description', 'date')
    search_fields = ('user__username', 'status', 'description')
    list_filter = ('status', 'date')
    readonly_fields = ('date',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_subscription_id', 'active')
    search_fields = ('user__username', 'stripe_subscription_id')
    list_filter = ('active',)
    readonly_fields = ('stripe_subscription_id', 'active')

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits')
    search_fields = ('user__username',)
    readonly_fields = ('credits',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'track', 'content', 'created_at')
    search_fields = ('user__username', 'track__title', 'content')
    list_filter = ('created_at',)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.track.title}"
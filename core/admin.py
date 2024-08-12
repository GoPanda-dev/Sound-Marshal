from django.contrib import admin
from .models import Payment, Subscription, Credit, Profile, Track, Campaign, Submission

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'date', 'description')
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'date')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_subscription_id', 'active')
    search_fields = ('user__username', 'stripe_subscription_id')
    list_filter = ('active',)

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits')
    search_fields = ('user__username',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'role', 'genre', 'role_selected')
    list_filter = ('role', 'genre', 'role_selected')
    search_fields = ('name', 'user__username', 'genre')
    readonly_fields = ('tokens',)

    fieldsets = (
        (None, {
            'fields': ('user', 'role', 'role_selected', 'tokens')
        }),
        ('Personal Info', {
            'fields': ('name', 'bio', 'genre')
        }),
        ('Social Media Links', {
            'fields': (
                'facebook_link', 'youtube_link', 'whatsapp_link', 'instagram_link',
                'tiktok_link', 'wechat_link', 'messenger_link', 'telegram_link',
                'viber_link', 'snapchat_link'
            )
        }),
    )

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'upload_date')
    search_fields = ('title', 'artist__username', 'genre')
    list_filter = ('genre', 'upload_date')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'target_genre', 'budget', 'created_at')
    search_fields = ('title', 'artist__username', 'target_genre')
    list_filter = ('target_genre', 'created_at')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('track', 'curator', 'status', 'submission_date', 'campaign')
    search_fields = ('track__title', 'curator__username', 'status')
    list_filter = ('status', 'submission_date', 'campaign')

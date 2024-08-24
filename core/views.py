from itertools import chain
import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import ProfileForm, UserForm, TrackForm, FeedbackForm, SubmissionForm, CampaignForm
from .models import Profile, Track, Submission, Campaign, Transaction, User, Comment
import stripe
from django.conf import settings
from .models import Payment, Subscription, Credit
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

load_dotenv()  # Load environment variables from .env file

# Load Stripe API keys
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def track_detail(request, track_id):
    track = get_object_or_404(Track, id=track_id)

    # Fetch related tracks by genre, excluding the current track
    related_tracks = Track.objects.filter(genre=track.genre).exclude(id=track.id)[:5]
    # Fetch comments related to the track
    comments = Comment.objects.filter(track=track).order_by('-created_at')

    context = {
        'track': track,
        'related_tracks': related_tracks,
        'comments': comments,
    }

    return render(request, 'core/track_detail.html', context)

def search(request):
    query = request.GET.get('q')
    if query:
        tracks = Track.objects.filter(
            Q(title__icontains=query) | Q(genre__icontains=query) | Q(description__icontains=query)
        )
        profiles = Profile.objects.filter(
            Q(name__icontains=query) | Q(bio__icontains=query) | Q(genre__icontains=query)
        )
    else:
        tracks = Track.objects.none()
        profiles = Profile.objects.none()

    context = {
        'query': query,
        'tracks': tracks,
        'profiles': profiles,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('core/partials/search_results_partial.html', context)
        return JsonResponse({'html': html})

    return render(request, 'core/search_results.html', context)

def create_payment_intent(request):
    try:
        intent = stripe.PaymentIntent.create(
            amount=1099,  # Amount in cents
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return JsonResponse({
            'client_secret': intent['client_secret']
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return JsonResponse({'status': 'invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return JsonResponse({'status': 'invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_failed_payment(payment_intent)
    # Add other event types as needed

    return JsonResponse({'status': 'success'}, status=200)

def handle_successful_payment(payment_intent):
    # Fetch user and amount from payment intent
    user_email = payment_intent['metadata']['user_email']
    user = User.objects.get(email=user_email)
    amount = payment_intent['amount'] / 100  # Convert cents to dollars

    # Create and save the Payment record
    Payment.objects.create(
        user=user,
        amount=amount,
        status='Completed',
        description=f"Purchase of {amount} credits"
    )

    # Update the user's wallet balance
    profile = user.profile
    profile.tokens += amount  # Assuming 1 dollar = 1 token
    profile.save()

def handle_failed_payment(payment_intent):
    # Implement any logic for failed payments, such as notifying the user
    pass

def payment_complete(request):
    return render(request, 'core/payment_complete.html')

@login_required
@csrf_exempt
def purchase_credits(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = int(data.get('amount'))  # Get the amount from the form (in dollars)
            cardholder_name = data.get('cardholder_name')
            amount_in_cents = amount * 100  # Convert to cents for Stripe

            # Create a PaymentIntent with the specified amount
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
                description=f"Credits for {request.user.username}",
                receipt_email=request.user.email,  # Send receipt to user's email
                metadata={'user_id': request.user.id, 'cardholder_name': cardholder_name},
            )

            # Return the client_secret to the frontend
            return JsonResponse({
                'client_secret': intent['client_secret']
            })

        except stripe.error.StripeError as e:
            # Handle Stripe-specific errors
            return JsonResponse({'error': str(e)}, status=400)

        except Exception as e:
            # Handle general errors
            return JsonResponse({'error': 'An error occurred while processing your request.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
@csrf_exempt
def confirm_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get('payment_intent_id')

            # Retrieve the PaymentIntent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == 'succeeded':
                # Update the user's token count
                profile = request.user.profile
                profile.tokens += intent.amount // 100  # Assuming 1 dollar = 1 token
                profile.save()

                # Record the payment
                Payment.objects.create(
                    user=request.user,
                    amount=intent.amount / 100,  # Convert from cents to dollars
                    status='Completed',
                    description=f"Purchase of {intent.amount / 100} credits"
                )

                # Log the transaction
                #Transaction.objects.create(
                #    user=request.user,
                #    transaction_type='credit',
                #    amount=intent.amount // 100,  # Assuming 1 dollar = 1 token
                #    description=f"Purchased {intent.amount // 100} credits"
                #)

                return JsonResponse({'success': True})

            else:
                return JsonResponse({'error': 'Payment not successful'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def subscribe(request):
    if request.method == 'POST':
        plan_id = request.POST['plan_id']  # ID of the plan

        customer = stripe.Customer.create(
            email=request.user.email,
            source=request.POST['stripeToken']
        )

        subscription = stripe.Subscription.create(
            customer=customer['id'],
            items=[{'plan': plan_id}]
        )

        Subscription.objects.create(
            user=request.user,
            stripe_subscription_id=subscription['id'],
        )

        return redirect('artist_dashboard')

    return render(request, 'core/subscribe.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@login_required
def manage_subscription(request):
    subscription = get_object_or_404(Subscription, user=request.user)

    if request.method == 'POST':
        subscription.cancel()
        return redirect('artist_dashboard')

    return render(request, 'core/manage_subscription.html', {
        'subscription': subscription
    })

@login_required
def wallet(request):
    payments = Payment.objects.filter(user=request.user).order_by('-date')
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Combine payments and transactions and sort by date
    history = sorted(chain(payments, transactions), key=lambda x: x.date, reverse=True)

    return render(request, 'core/wallet.html', {
        'balance': request.user.profile.tokens,
        'history': history,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })

@login_required
def submit_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    curators = User.objects.filter(profile__role='curator')

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        curator_id = request.POST.get('curator_id')
        curator = get_object_or_404(User, id=curator_id)

        # Check if the artist has enough tokens
        if request.user.profile.tokens > 0:
            if form.is_valid():
                # Debugging: Verify the form is valid and is being saved correctly
                print("Form is valid.")
                
                submission = form.save(commit=False)
                submission.track = track
                submission.curator = curator
                submission.save()

                # Deduct a token from the artist's profile
                request.user.profile.tokens -= 1
                request.user.profile.save()

                # Log the transaction
                Transaction.objects.create(
                    user=request.user,
                    transaction_type='debit',
                    amount=1,
                    description=f"Submission of {track.title} to {curator.profile.name}"
                )

                return redirect('artist_dashboard')
            else:
                # Debugging: Print out form errors if not valid
                print("Form is not valid:", form.errors)
        else:
            form.add_error(None, 'You do not have enough tokens to submit this track.')

    else:
        form = SubmissionForm()

    return render(request, 'core/submit_track.html', {'track': track, 'form': form, 'curators': curators})

def upload_track(request):
    if request.method == 'POST':
        form = TrackForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('artist_dashboard')
    else:
        form = TrackForm()
    return render(request, 'upload_track.html', {'form': form})

@login_required
def artist_dashboard(request):
    tracks = Track.objects.filter(artist=request.user)
    submissions = Submission.objects.filter(track__artist=request.user)

    if request.method == 'POST':
        form = TrackForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.artist = request.user
            track.save()
            return redirect('artist_dashboard')
    else:
        form = TrackForm()

    context = {
        'tracks': tracks,
        'submissions': submissions,
        'form': form,
    }
    return render(request, 'core/artist_dashboard.html', context)

@login_required
def curator_dashboard(request):
    submissions = Submission.objects.filter(curator=request.user)
    genre_filter = request.GET.get('genre')
    if genre_filter:
        submissions = submissions.filter(track__genre=genre_filter)

    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        feedback = request.POST.get('feedback')
        rating = request.POST.get('rating')
        voice_feedback = request.FILES.get('voice_feedback')
        video_feedback = request.FILES.get('video_feedback')

        submission = get_object_or_404(Submission, id=submission_id)
        submission.feedback = feedback
        submission.rating = rating
        submission.voice_feedback = voice_feedback
        submission.video_feedback = video_feedback
        submission.status = 'reviewed'
        submission.save()
        return redirect('curator_dashboard')

    context = {
        'submissions': submissions,
    }
    return render(request, 'core/curator_dashboard.html', context)

@login_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(artist=request.user)
    return render(request, 'core/campaign_list.html', {'campaigns': campaigns})

@login_required
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    return render(request, 'core/campaign_detail.html', {'campaign': campaign})

@login_required
def submission_list(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    submissions = Submission.objects.filter(campaign=campaign)
    return render(request, 'core/submission_list.html', {'campaign': campaign, 'submissions': submissions})

@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return render(request, 'core/submission_detail.html', {'submission': submission})

@login_required
def provide_feedback(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)  # Save the form but don't commit to the database yet
            submission.status = 'reviewed'  # Update the status to 'reviewed'
            submission.save()  # Save the updated submission to the database
            return redirect('curator_dashboard')  # Redirect to the dashboard or any other page
    else:
        form = FeedbackForm(instance=submission)

    return render(request, 'provide_feedback.html', {'form': form, 'submission': submission})

@login_required
def campaign_overview(request):
    campaigns = Campaign.objects.filter(artist=request.user)
    return render(request, 'core/campaign_overview.html', {'campaigns': campaigns})

def profile_detail(request, slug):
    profile = get_object_or_404(Profile, slug=slug)
    
    if request.method == "POST":
        # Toggle follow/unfollow
        if profile.followers.filter(id=request.user.id).exists():
            profile.followers.remove(request.user)
        else:
            profile.followers.add(request.user)
        
        return redirect('profile_detail', slug=slug)
    
    # Check if the current user is following this profile
    is_following = profile.followers.filter(id=request.user.id).exists()
    
    return render(request, 'core/profile_detail.html', {
        'profile': profile,
        'is_following': is_following,
    })

@login_required
def account_settings(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        # Debugging: Check if forms are valid and print errors if any
        if not user_form.is_valid():
            print("User Form Errors:", user_form.errors)
        if not profile_form.is_valid():
            print("Profile Form Errors:", profile_form.errors)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Your account settings have been updated.")
            return redirect('profile_detail', slug=profile.slug)
        else:
            messages.error(request, "There was an error with your submission.")

    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'core/account_settings.html', context)

@login_required
def select_role(request):
    if request.method == 'POST':
        selected_role = request.POST.get('role')
        profile = request.user.profile

        if selected_role in ['artist', 'curator', 'fan']:
            profile.role = selected_role
            profile.role_selected = True
            profile.save()

            if selected_role == 'artist':
                return redirect('create_artist_profile')
            elif selected_role == 'curator':
                return redirect('create_curator_label_profile')
            elif selected_role == 'fan':
                return redirect('create_fan_profile')

    return render(request, 'core/select_role.html')

@login_required
def create_artist_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.role_selected = True
            profile.role = 'artist'
            profile.save()
            return redirect('profile_detail', slug=profile.slug)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'core/create_artist_profile.html', {'form': form})

@login_required
def create_curator_label_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.role_selected = True
            profile.role = 'curator'
            profile.save()
            return redirect('profile_detail', slug=profile.slug)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'core/create_curator_label_profile.html', {'form': form})

@login_required
def create_fan_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.role_selected = True
            profile.role = 'fan'
            profile.save()
            return redirect('profile_detail', slug=profile.slug)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'core/create_fan_profile.html', {'form': form})

@login_required
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.artist = request.user
            selected_tracks = form.cleaned_data['tracks']
            targeted_curators = form.cleaned_data['curators_targeted']
            total_submissions = len(selected_tracks) * len(targeted_curators)

            # Check if the artist has enough tokens
            if request.user.profile.tokens >= total_submissions:
                campaign.save()
                form.save_m2m()  # Save the many-to-many data for tracks and curators_targeted

                # Create submissions and deduct tokens
                for curator in campaign.curators_targeted.all():
                    for track in campaign.tracks.all():
                        Submission.objects.create(
                            track=track,
                            curator=curator,
                            campaign=campaign
                        )
                        request.user.profile.tokens -= 1
                        request.user.profile.save()

                        # Log the transaction
                        Transaction.objects.create(
                            user=request.user,
                            transaction_type='debit',
                            amount=1,
                            description=f"Submission of {track.title} to {curator.profile.name} in campaign {campaign.title}"
                        )

                return redirect('artist_dashboard')
            else:
                form.add_error(None, f'You do not have enough tokens to create this campaign. You need {total_submissions} tokens.')

    else:
        form = CampaignForm()

    return render(request, 'core/create_campaign.html', {'form': form})

@login_required
def toggle_like_track(request):

    try:
        data = json.loads(request.body)
        track_id = data.get('track_id')
        
        track = Track.objects.get(id=track_id)
        profile = request.user.profile
        
        if profile.liked_tracks.filter(id=track_id).exists():
            # Track is already liked, so we remove it
            profile.liked_tracks.remove(track)
            liked = False
        else:
            # Track is not liked, so we add it
            profile.liked_tracks.add(track)
            liked = True
        
        return JsonResponse({'success': True, 'liked': liked})
    except Track.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Track not found'})


@login_required
def check_if_liked(request, track_id):
    try:
        track = Track.objects.get(id=track_id)
        profile = request.user.profile
        
        is_liked = profile.liked_tracks.filter(id=track_id).exists()
        
        return JsonResponse({'is_liked': is_liked})
    except Track.DoesNotExist:
        return JsonResponse({'is_liked': False, 'message': 'Track not found'})

@login_required
@require_POST
def like_track(request):
    try:
        data = json.loads(request.body)
        track_id = data.get('track_id')
        print(f"Received track ID: {track_id}")  # Debugging
        
        track = Track.objects.get(id=track_id)
        profile = request.user.profile
        
        # Add the track to the user's liked tracks
        profile.liked_tracks.add(track)
        print(f"Track {track_id} added to {request.user.username}'s likes.")  # Debugging
        
        return JsonResponse({'success': True})
    except Track.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Track not found'})
    except Exception as e:
        print(f"Error liking track: {str(e)}")  # Debugging
        return JsonResponse({'success': False, 'message': str(e)})
    
@login_required
def add_comment(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    
    if request.method == 'POST':
        content = request.POST.get('comment')
        if content:
            Comment.objects.create(
                user=request.user,
                track=track,
                content=content,
            )
    
    return redirect('track_detail', track_id=track.id)

@login_required
def explore(request):
    user = request.user
    user_profile = user.profile
    user_genres = [genre.strip() for genre in user_profile.genre.split(',')]  # Clean up genre strings
    user_likes = user_profile.liked_tracks.values_list('id', flat=True)  # Get a list of liked track IDs
    liked_artists = user_profile.liked_tracks.values_list('artist_id', flat=True).distinct()  # Get IDs of liked artists

    # Fetch tracks related to the user's genre and exclude already liked tracks
    related_tracks = Track.objects.filter(
        Q(genre__in=user_genres) | Q(artist_id__in=liked_artists)
    ).exclude(id__in=user_likes).select_related('artist').order_by('-upload_date')
    
    # Fetch profiles related to the user's genre, excluding the current user
    related_profiles = Profile.objects.filter(
        genre__in=user_genres
    ).exclude(user=user).select_related('user').annotate(track_count=Count('user__track')).order_by('-track_count')

    # Apply pagination to the related tracks and profiles
    track_paginator = Paginator(related_tracks, 10)  # Show 10 tracks per page
    profile_paginator = Paginator(related_profiles, 10)  # Show 10 profiles per page

    track_page_number = request.GET.get('track_page')
    profile_page_number = request.GET.get('profile_page')

    track_page_obj = track_paginator.get_page(track_page_number)
    profile_page_obj = profile_paginator.get_page(profile_page_number)

    context = {
        'track_page_obj': track_page_obj,
        'profile_page_obj': profile_page_obj,
    }

    return render(request, 'core/explore.html', context)

def home(request):
    recommended_curators = []
    recommended_artists = []
    
    if request.user.is_authenticated:
        if request.user.profile.is_artist:
            recommended_curators = User.objects.filter(profile__role='curator').order_by('?')[:3]
        elif request.user.profile.is_curator:
            recommended_artists = User.objects.filter(profile__role='artist').order_by('?')[:3]

    return render(request, 'core/home.html', {
        'recommended_curators': recommended_curators,
        'recommended_artists': recommended_artists,
    })

from itertools import chain
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, UserForm, TrackForm, FeedbackForm, SubmissionForm, CampaignForm
from .models import Profile, Track, Submission, Campaign, Transaction, User
import stripe
from django.conf import settings
from .models import Payment, Subscription, Credit
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from django.contrib import messages

load_dotenv()  # Load environment variables from .env file

# Load Stripe API keys
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@login_required
@csrf_exempt
def purchase_credits(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')  # Get the token from the form
        amount = int(request.POST.get('amount'))  # Get the amount from the form (in dollars)
        amount_in_cents = amount * 100  # Convert to cents for Stripe

        try:
            charge = stripe.Charge.create(
                amount=amount_in_cents,
                currency='usd',
                description=f"Credits for {request.user.username}",
                source=token  # Pass the token here
            )

            # Create and save the Payment record
            Payment.objects.create(
                user=request.user,
                amount=amount,
                status='Completed',  # Assuming the payment was successful
                description=f"Purchase of {amount} credits"
            )

            # Update the user's wallet balance
            profile = request.user.profile
            profile.tokens += amount  # Assuming 1 dollar = 1 token
            profile.save()

            return redirect('wallet')
        except stripe.error.StripeError as e:
            # Handle the error
            Payment.objects.create(
                user=request.user,
                amount=amount,
                status='Failed',
                description=str(e)
            )
            return render(request, 'core/wallet.html', {'error': str(e), 'balance': request.user.profile.tokens})

    return redirect('wallet')

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
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
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
    return render(request, 'core/profile_detail.html', {'profile': profile})

@login_required
def account_settings(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        # Debugging: Print form errors if not valid
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
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'core/account_settings.html', context)

@login_required
def select_role(request):
    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        
        if role == 'artist':
            profile.role_selected = True
            profile.role = 'artist'
            profile.save()
            return redirect('create_artist_profile')
        elif role == 'curator':
            profile.role_selected = True
            profile.role = 'curator'
            profile.save()
            return redirect('create_curator_label_profile')

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
            return redirect('profile_detail', pk=profile.pk)
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
            return redirect('profile_detail', pk=profile.pk)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'core/create_curator_label_profile.html', {'form': form})

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

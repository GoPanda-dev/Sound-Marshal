from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, UserForm, TrackForm, FeedbackForm, SubmissionForm, CampaignForm
from .models import Profile, Track, Submission, Campaign, User

@login_required
def wallet(request):
    profile = request.user.profile
    return render(request, 'core/wallet.html', {'balance': profile.tokens})

@login_required
def submit_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    curators = User.objects.filter(profile__role='curator')

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        curator_id = request.POST.get('curator_id')
        curator = get_object_or_404(User, id=curator_id)

        if form.is_valid():
            submission = form.save(commit=False)
            submission.track = track
            submission.curator = curator
            submission.save()
            return redirect('artist_dashboard')
    else:
        form = SubmissionForm()

    return render(request, 'core/submit_track.html', {'track': track, 'form': form, 'curators': curators})

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
            form.save()
            return redirect('curator_dashboard')
    else:
        form = FeedbackForm(instance=submission)

    return render(request, 'core/provide_feedback.html', {'form': form, 'submission': submission})

@login_required
def campaign_overview(request):
    campaigns = Campaign.objects.filter(artist=request.user)
    return render(request, 'core/campaign_overview.html', {'campaigns': campaigns})

@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    return render(request, 'core/profile_detail.html', {'profile': profile})

@login_required
def account_settings(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.role_selected = True  # Mark that the user has selected a role
            profile.save()
            return redirect('account_settings')

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
            campaign.save()
            return redirect('artist_dashboard')
    else:
        form = CampaignForm()

    return render(request, 'core/create_campaign.html', {'form': form})

def home(request):
    return render(request, 'core/home.html')

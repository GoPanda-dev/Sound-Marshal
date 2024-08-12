from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, UserForm, TrackForm, FeedbackForm, SubmissionForm
from .models import Profile, Track, Submission, User

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
        submission = Submission.objects.get(id=submission_id)
        submission.feedback = feedback
        submission.status = 'reviewed'
        submission.save()
        return redirect('curator_dashboard')

    context = {
        'submissions': submissions,
    }
    return render(request, 'core/curator_dashboard.html', context)

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

def home(request):
    return render(request, 'core/home.html')

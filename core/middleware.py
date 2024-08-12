from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile

class ProfileCreationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Ensure the profile exists or create it
            profile, created = Profile.objects.get_or_create(user=request.user)

            if not profile.role_selected:
                # If profile exists but the role is not selected, redirect to the role selection page
                if request.path != reverse('select_role') and not request.path.startswith('/logout'):
                    return redirect('select_role')

        return self.get_response(request)

# middleware.py

from django.utils.deprecation import MiddlewareMixin

class ThemeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        theme = request.COOKIES.get('theme', 'light')
        request.theme = theme

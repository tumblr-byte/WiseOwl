from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from home.models import User


def simple_login(request):
    """
    Simple username-based login/signup
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        
        # Validate username
        if not username:
            messages.error(request, 'Please enter a username')
            return redirect('home:landing')
        
        if len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters')
            return redirect('home:landing')
        
        # Get or create user with this username
        user, created = User.objects.get_or_create(
            username=username.lower(),
            defaults={
                'email': f'{username.lower()}@fibo.local',
            }
        )
        
        # Log the user in
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Redirect to home page
        if created:
            messages.success(request, f'Welcome {username}! Your account has been created.')
        else:
            messages.success(request, f'Welcome back {username}!')
        
        return redirect('home:home')
    
    # If GET request, redirect to landing
    return redirect('home:landing')

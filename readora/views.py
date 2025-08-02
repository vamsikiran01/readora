from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.contrib import messages
from datetime import date
import traceback
from django.core.mail import send_mail

from .models import RegisteredUser, IssuedBook  # Add Book if needed

# Home Page
def index(request):
    return render(request, 'index.html')

# Dashboard Page
def dashboard(request):
    return render(request, 'dashboard.html')

# Issue/Return Books Page
def issue_books(request):
    return render(request, 'issuebooks.html')

# Search Books Page
def search_books(request):
    return render(request, 'searchbooks.html')

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

# Register View
def register(request):
    if request.method == "POST":
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        password = request.POST.get('password')

        username = email.split('@')[0]

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered'})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = full_name
            user.save()

            messages.success(request, f"Registration successful! Your username is '{username}'")
            return redirect('login')

        except Exception as e:
            print("❌ ERROR DURING REGISTRATION:")
            traceback.print_exc()
            return render(request, 'register.html', {'error': 'Error during registration'})

    return render(request, 'register.html')

# Forgot Password Page
# Simulated password reset — replace with real token logic in production
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = get_random_string(length=32)
            reset_link = f"http://127.0.0.1:8000/reset-password/{token}/"
            send_mail(
                'Password Reset Request',
                f'Hello {user.username}, click the link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No user is registered with this email.")
    return render(request, 'forgot_password.html')

# Reminders Page
def reminders(request):
    today = date.today()
    issued_books = IssuedBook.objects.filter(user=request.user, returned=False)
    return render(request, 'reminders.html', {
        'issued_books': issued_books,
        'today': today
    })

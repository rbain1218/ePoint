from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import RegisterForm, VerifyOTPForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .models import EmailOTP

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
            else:
                otp = EmailOTP.generate_otp()
                EmailOTP.objects.create(email=email, otp=otp, purpose='register')
                send_mail('E-Point Registration OTP', f'Your OTP is: {otp}', None, [email])
                request.session['pending_user'] = {'username': username, 'email': email, 'password': password}
                messages.success(request, 'OTP sent to your email.')
                return redirect('accounts:verify')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify(request):
    pending = request.session.get('pending_user')
    if not pending:
        messages.error(request, 'No registration in progress.')
        return redirect('accounts:register')
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = form.cleaned_data['otp']
            match = EmailOTP.objects.filter(email=email, otp=otp, purpose='register').last()
            if match:
                user = User.objects.create_user(
                    username=pending['username'], email=pending['email'], password=pending['password']
                )
                del request.session['pending_user']
                messages.success(request, 'Email verified. You can login now.')
                return redirect('accounts:login')
            messages.error(request, 'Invalid OTP.')
    else:
        form = VerifyOTPForm(initial={'email': pending['email']})
    return render(request, 'accounts/verify.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, username=form.cleaned_data['username'], password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                messages.success(request, 'Logged in.')
                return redirect('shop:home')
            messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out.')
    return redirect('shop:home')

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not User.objects.filter(email=email).exists():
                messages.error(request, 'No user with that email.')
            else:
                otp = EmailOTP.generate_otp()
                EmailOTP.objects.create(email=email, otp=otp, purpose='reset')
                send_mail('E-Point Password Reset OTP', f'Your OTP is: {otp}', None, [email])
                messages.success(request, 'Reset OTP sent. Enter OTP to set new password.')
                return redirect('accounts:reset_password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot.html', {'form': form})

def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = form.cleaned_data['otp']
            new_password = form.cleaned_data['new_password']
            match = EmailOTP.objects.filter(email=email, otp=otp, purpose='reset').last()
            if match:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset. Login now.')
                return redirect('accounts:login')
            messages.error(request, 'Invalid OTP.')
    else:
        form = ResetPasswordForm()
    return render(request, 'accounts/reset.html', {'form': form})

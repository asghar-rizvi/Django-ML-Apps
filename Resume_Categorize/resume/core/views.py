import PyPDF2
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import userInfo
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from io import BytesIO
import numpy as np
import logging
from pathlib import Path
from django.contrib.auth import update_session_auth_hash
import json 
from .preprocess import predict_class, load_models

load_models()

PROJECT_ROOT = Path(__file__).parent.parent 
classes_labels_filename = 'label_mapping.json' 
labels_path = PROJECT_ROOT / 'class_labels' / classes_labels_filename 

try:
    if labels_path.exists():
        with open(labels_path, 'r') as file:
            job_titles = json.load(file)
    else:
        print('file not exist')
except FileNotFoundError as e:
    logging.error(f"Model loading failed: {e}")


def class_label(num):
    if str(num) in job_titles:
        return job_titles[str(num)]
    else:
        return "Invalid number"


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:  # Ensure extracted text is not None
            text += extracted_text + '\n'
    return text


from django.http import JsonResponse

@login_required
def home_page(request):
    if request.method == 'POST':
        if 'resume' in request.FILES:
            pdf_file = request.FILES['resume']
            text = extract_text_from_pdf(pdf_file)
            
            predict = predict_class(text)  
            category = class_label(predict[0])  

            return JsonResponse({"result": category})
        else:
            return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

    return render(request, 'home.html')


def register_user(request):
    if request.method == 'POST':
        data = request.POST
        first_name = data.get('firstname')
        last_name = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')

        if User.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists. Please sign in.')
            return redirect('login')

        if User.objects.filter(email=email).exists():
            messages.warning(request, 'Email already registered. Please sign in.')
            return redirect('login')

        if password1 != password2:
            messages.warning(request, 'Passwords do not match!')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,  #
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, 'Account successfully created! You can now log in.')
        return redirect('login')

    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home_page')  
        else:
            messages.warning(request, 'Invalid username or password.')
            return redirect('login')  

    return render(request, 'login.html')

@login_required
def update_user(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.username = username

        # If a new password is provided, update it
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)  # Prevents logout after password change
        
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("update")  # Redirect to the same page to see updated info

    return render(request, "update.html", {"user": request.user})

@login_required
def logout_user(request):
    logout(request)
    return redirect('register')


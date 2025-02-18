import fitz  
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import userInfo
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from io import BytesIO
import numpy as np
import pickle
import logging
from pathlib import Path
import json 

PROJECT_ROOT = Path(__file__).parent.parent 

model_filename = 'resume_classifier.pkl'
model_path = PROJECT_ROOT / 'model' / model_filename 

try:
    if model_path.exists():
        # Open the file in binary read mode
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logging.info(f"Model loaded successfully from {model_path}")
    else:
        raise FileNotFoundError(f"Model file not found at {model_path}")
except FileNotFoundError as e:
    logging.error(f"Model loading failed: {e}")
except Exception as e:
    logging.error(f"An error occurred while loading the model: {e}")

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
    text = ""
    with fitz.open(stream=BytesIO(file.read()), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

from django.http import JsonResponse

@login_required
def home_page(request):
    if request.method == 'POST':
        if 'resume' in request.FILES:
            pdf_file = request.FILES['resume']
            text = extract_text_from_pdf(pdf_file)
            
            predict = model.predict([text])  # Ensure input is in a list format
            category = class_label(predict[0])  # Extract single prediction

            return JsonResponse({'success': True, 'data': category})
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

def update_user(request):
    
    
    return render(request, 'update.html')

def logout_user(request):
    logout(request)
    return redirect('register')


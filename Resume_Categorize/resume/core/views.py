from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from .preprocess import *

load_models()

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


def predict_job_placement(request):
    if request.method == "POST":
        ssc_percentage = float(request.POST["ssc_percentage"])
        hsc_percentage = float(request.POST["hsc_percentage"])
        degree_percentage = float(request.POST["degree_percentage"])
        emp_test_percentage = float(request.POST["emp_test_percentage"])
        mba_percent = float(request.POST["mba_percent"])

        gender_M = 1 if request.POST["gender"] == 'M' else 0
        ssc_board_Others = 1 if request.POST["ssc_board"] == 'Others' else 0
        hsc_board_Others = 1 if request.POST["hsc_board"] == 'Others' else 0

        hsc_subject = request.POST["hsc_subject"]
        hsc_subject_Commerce = 1 if hsc_subject == 'Commerce' else 0
        hsc_subject_Science = 1 if hsc_subject == 'Science' else 0

        undergrad_degree = request.POST["undergrad_degree"]
        undergrad_degree_Others = 1 if undergrad_degree == 'Others' else 0
        undergrad_degree_Sci_Tech = 1 if undergrad_degree == 'Sci&Tech' else 0

        work_experience_Yes = 1 if request.POST["work_experience"] == 'Yes' else 0

        specialisation_Mkt_HR = 1 if request.POST["specialisation"] == 'Mkt&HR' else 0

        features = [[
            ssc_percentage, hsc_percentage, degree_percentage,
            emp_test_percentage, mba_percent, gender_M, ssc_board_Others,
            hsc_board_Others, hsc_subject_Commerce, hsc_subject_Science,
            undergrad_degree_Others, undergrad_degree_Sci_Tech,
            work_experience_Yes, specialisation_Mkt_HR
        ]]
        
        prediction = predict_placement(features) 

        return JsonResponse({"result": prediction})

    return render(request, "job_placement.html")

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
            return redirect('resume')  
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


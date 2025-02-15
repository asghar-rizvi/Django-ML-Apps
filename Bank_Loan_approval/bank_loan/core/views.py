from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import joblib

model = joblib.load("model/load_status_model.pkl")

@login_required
@csrf_exempt
def predict(request):
    if request.method == "POST":
        try:
            credit_score = float(request.POST.get("credit_score"))
            annual_income = float(request.POST.get("annual_income"))
            years_in_current_job = float(request.POST.get("years_in_current_job"))

            # Format data for model
            input_data = np.array([[credit_score, annual_income, years_in_current_job]])

            # Make prediction
            prediction = model.predict(input_data)[0]
            
            # Convert prediction to human-readable response
            prediction_text = "Approved" if prediction == 1 else "Rejected"

            return JsonResponse({"result": prediction_text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


def registration_user(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        email = data.get('email')
        password1 = data.get('password1') 
        password2 = data.get('password2') 
        
        user = User.objects.filter(username=username )
        if user.exists():
            messages.warning(request, "Username is already taken")
            return redirect('/registeration-user/')
       
        user2 = User.objects.filter(email = email)
        if user2.exists():
            messages.warning(request, "Email is already taken")
            return redirect('/registeration-user/')
        
        if password1 != password2:
            messages.error(request, 'Passoword does not match')
            return redirect('/registeration-user/')
        else :
            user = User.objects.create(
                username = username,
                email = email
            )
            user.set_password(password1)
            user.save()
            
            messages.success(request, "Account Successfully Created")
            return redirect('/login-user/')
    return render(request, 'registration.html')

def login_user(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        
        user = User.objects.filter(username=username )
        if user.exists():
             user = authenticate(username = username, password = password)
             if user is None :
                messages.error(request, 'Password is not valid')
                return redirect('/login-user/')
             else :
                login(request, user)
                return redirect('/predict/')
        else:
            
            messages.warning(request, "User is not registered")
            return redirect('/login-user/')
           
    return render(request, 'login.html')
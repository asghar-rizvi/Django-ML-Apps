from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import numpy as np
import joblib
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "core", "model", "loan_status_model.pkl")

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

@login_required
def predict_page(request):
    if request.method == "POST":
        if model is None:
            print("Model is not loaded!")  
            return JsonResponse({"error": "Model not loaded"}, status=500)

        try:
            current_loan_amount = float(request.POST.get("current_loan_amount", "0"))
            max_open_credit = float(request.POST.get("max_open_credit", "0"))
            credit_score = float(request.POST.get("credit_score", "0"))
            annual_income = float(request.POST.get("annual_income", "0"))

            years_in_current_job = request.POST.get("years_in_current_job", "0")
            years_in_current_job = float(years_in_current_job.replace("+", "").strip())  

            term_str = request.POST.get("term", "").strip()
            term = 1 if term_str == "Long Term" else 0  

            monthly_debt = float(request.POST.get("monthly_debt", "0"))
            years_credit_history = float(request.POST.get("years_credit_history", "0"))
            num_open_accounts = float(request.POST.get("num_open_accounts", "0"))
            num_credit_problems = float(request.POST.get("num_credit_problems", "0"))  
            current_credit_balance = float(request.POST.get("current_credit_balance", "0"))
            bankruptcies = float(request.POST.get("bankruptcies", "0"))
            tax_liens = float(request.POST.get("tax_liens", "0"))

            home_ownership = request.POST.get("home_ownership", "").strip()
            home_mortgage = home_ownership == "Mortgage"
            home_own = home_ownership == "Own Home"
            home_rent = home_ownership == "Rent"

            input_data = np.array([[
                current_loan_amount, 
                term,
                credit_score, 
                annual_income,
                years_in_current_job, 
                monthly_debt, 
                years_credit_history, 
                num_open_accounts,
                num_credit_problems, 
                current_credit_balance, 
                max_open_credit, 
                bankruptcies,
                tax_liens, 
                home_mortgage,
                home_own,
                home_rent
            ]], dtype=object) 

            prediction = model.predict(input_data)[0]
            prediction_text = "Approved" if prediction == 1 else "Rejected"
            
            try:
                user_prediction = predict_user.objects.get(user=request.user)
                user_prediction.credit_card_score = credit_score 
                user_prediction.loan_Status = prediction_text
                user_prediction.save()

            except predict_user.DoesNotExist:
                predict_user.objects.create(
                    user=request.user, 
                    credit_card_score=credit_score, 
                    loan_Status=prediction_text
                )
            except Exception as e: 
                print(f"Database update error: {e}")
                
            return JsonResponse({"result": prediction_text})

        except ValueError as ve:  
            print(f"❌ ValueError: {ve}") 
            return JsonResponse({"error": f"Invalid input data: {ve}"}, status=400)

        except Exception as e:
            print(f"❌ General Error: {e}")  
            return JsonResponse({"error": "An error occurred during prediction."}, status=500)

    return render(request, 'index.html')


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

def logout_user(request):
    logout(request)
    return redirect('/login-user/')
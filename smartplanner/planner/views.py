from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm, CustomRegisterForm, UpdateProfileForm, TripForm, DestinationRecommendationForm
from .models import Trip, Itinerary,  RecommendationLog

import os
import joblib
import pandas as pd
from django.conf import settings
import google.generativeai as genai

# === Configure Gemini API ===
print("API KEY:", settings.GEMINI_API_KEY)
genai.configure(api_key=settings.GEMINI_API_KEY)

# === ML paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'recommendation_model.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'ml', 'bud_encoder.pkl')  # ✅ renamed here
DATA_PATH = os.path.join(BASE_DIR, 'data', 'worldwide_travel_cities.csv')


# === Homepage ===
def home(request):
    return render(request, 'home.html')

# === Login ===
def login_user(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('dashboard')

    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

# === Register ===
def register_user(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already registered and logged in.")
        return redirect('dashboard')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

# === Logout ===
def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# === Dashboard ===
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# === Update Profile ===
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, 'update_profile.html', {'form': form})

# === Trip Planning (Gemini Itinerary Generator) ===
@login_required
def plan_trip(request):
    INTEREST_OPTIONS = [
        'adventure', 'culture', 'food', 'shopping', 'nature',
        'history', 'nightlife', 'sports', 'beaches'
    ]

    selected_interests = request.POST.getlist('interests') if request.method == 'POST' else []

    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.interests = ','.join(selected_interests)
            trip.save()

            try:
                model = genai.GenerativeModel('gemini-pro')
                prompt = (
                    f"Plan a 3-day travel itinerary for {trip.destination} from {trip.start_date} to {trip.end_date}. "
                    f"The user has a budget of ₹{trip.budget}. Their interests are: {', '.join(selected_interests)}. "
                    "Suggest places to visit, activities, and a rough schedule for each day."
                )

                response = model.generate_content(prompt)
                generated_itinerary = getattr(response, 'text', None)
                if not generated_itinerary:
                    generated_itinerary = "Gemini API did not return any text. Please try again later."

            except Exception as e:
                print("Gemini Error:", e)
                generated_itinerary = "There was an error generating your itinerary. Please try again later."

            Itinerary.objects.create(trip=trip, details=generated_itinerary)
            return redirect('view_itinerary', trip_id=trip.id)

    else:
        form = TripForm()

    return render(request, 'plan.html', {
        'form': form,
        'interests': INTEREST_OPTIONS,
        'selected_interests': selected_interests
    })

@login_required
def view_itinerary(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    interests_list = [i.strip().capitalize() for i in trip.interests.split(',')] if trip.interests else []

    try:
        itinerary = Itinerary.objects.get(trip=trip)
        itinerary_text = itinerary.details
    except Itinerary.DoesNotExist:
        itinerary_text = "No itinerary has been generated for this trip yet."

    return render(request, 'itinerary.html', {
        'trip': trip,
        'itinerary_text': itinerary_text,
        'interests_list': interests_list,
    })

## === Static Interest List ===
INTERESTS = [
    'culture', 'adventure', 'nature', 'beaches', 'nightlife',
    'cuisine', 'wellness', 'urban', 'seclusion'
]

# === Model-based Recommendation ===
def recommend_destinations(request):
    recommendations = []
    selected_interests = []

    if request.method == 'POST':
        form = DestinationRecommendationForm(request.POST)
        if form.is_valid():
            destination = form.cleaned_data['destination']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            budget = form.cleaned_data['budget']
            selected_interests = request.POST.getlist('interests')

            # === Load data & model ===
            df = pd.read_csv(DATA_PATH)
            model = joblib.load(MODEL_PATH)
            le_budget = joblib.load(ENCODER_PATH)

            # === Clean and prepare data ===
            df = df.dropna(subset=[
                'culture', 'adventure', 'nature', 'beaches', 'nightlife',
                'cuisine', 'wellness', 'urban', 'seclusion', 'budget_level'
            ])
            df['budget_level'] = df['budget_level'].str.strip().str.lower()
            df['budget_level'] = df['budget_level'].replace({
                'mid-range': 'medium', 'budget': 'low', 'luxury': 'luxury'
            })
            df['budget_level_encoded'] = le_budget.transform(df['budget_level'])

            # === Define interest columns used in model training ===
            interest_columns = [
                'culture', 'adventure', 'nature', 'beaches', 'nightlife',
                'cuisine', 'wellness', 'urban', 'seclusion'
            ]

            # === Build user input vector ===
            user_input = {
                col: 5 if col in selected_interests else 1
                for col in interest_columns
            }
            # Budget category logic
            if budget < 15000:
                user_input['budget_level_encoded'] = le_budget.transform(['low'])[0]
            elif budget > 50000:
                user_input['budget_level_encoded'] = le_budget.transform(['luxury'])[0]
            else:
                user_input['budget_level_encoded'] = le_budget.transform(['medium'])[0]

            # === Predict user preference score with model ===
            input_vector = pd.DataFrame([user_input])
            predicted_score = model.predict(input_vector)[0]

            # === Score each city using interest overlap ===
            df['match_score'] = df[interest_columns].apply(
                lambda row: sum([row[col] for col in selected_interests]) / len(selected_interests)
                if selected_interests else 0,
                axis=1
            )

            # === Rank cities based on match_score and recommend top 3 ===
            top_cities = df.sort_values(by='match_score', ascending=False).head(3)
            recommendations = list(top_cities['city']) if 'city' in df.columns else list(top_cities.index[:3])

    else:
        form = DestinationRecommendationForm()

    return render(request, 'destination_recommendation.html', {
        'form': form,
        'interests': INTERESTS,
        'selected_interests': selected_interests,
        'recommendations': recommendations,
    })

@login_required
def recommendation_history(request):
    logs = RecommendationLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'recommendation_history.html', {
        'logs': logs
    })

@login_required
def recommendation_history(request):
    trips = Trip.objects.filter(user=request.user).order_by('-start_date')
    trip_data = []

    for trip in trips:
        itinerary = Itinerary.objects.filter(trip=trip).first()
        trip_data.append({
            'trip': trip,
            'itinerary': itinerary.details if itinerary else "No itinerary available."
        })

    return render(request, 'history.html', {'trip_data': trip_data})

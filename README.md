# 🌍 SmartPlanner — AI-Powered Travel Planning App

SmartPlanner is a **Django-based AI travel assistant** that helps users plan their perfect trip by combining the power of **machine learning** and **generative AI**. From destination recommendations to 3-day personalized itineraries, SmartPlanner makes travel planning intelligent, intuitive, and effortless.

---

## 🧭 Key Features

### 🔐 Authentication & User Profiles
- User **registration, login/logout**
- Secure **password change & update profile**
- Flash messages and session support

### 🤖 ML-Powered Destination Recommendation
- Predicts top destinations based on:
  - Budget (low / medium / luxury)
  - User interests (culture, adventure, beaches, nightlife, etc.)
- Uses a trained **Scikit-learn classifier**

### 🧠 AI-Based Itinerary Generation (via Gemini Pro)
- Creates **3-day itineraries** tailored to:
  - Destination
  - Budget
  - Travel dates
  - Interests
- Powered by **Google Gemini Pro API**

### 🧾 Smart Storage
- Saved **itineraries** and **recommendations** are linked to user accounts
- Accessible any time from your dashboard

### 👤 Profile Management
- View/edit your profile
- Change password with confirmation
- Dashboard showing saved plans

---

## 🛠️ Tech Stack

| Category       | Technology                                  |
|----------------|---------------------------------------------|
| Backend        | Python 3.9+, Django 4.x                     |
| Frontend       | HTML, CSS, Bootstrap                        |
| AI/ML          | Gemini (Google), Scikit-learn, Pandas   |
| Storage        | SQLite / PostgreSQL                         |
| Hosting        | Works with Heroku, Render, etc.             |

---

## 🧠 ML Recommendation Logic

- **Input**: User interests + budget
- **Preprocessing**: Categorical budget encoding, interest scoring
- **Model**: Trained classifier using city-level features
- **Output**: Top 3 ranked cities by predicted match score

## 📁 Project Structure
smartplanner/
├── planner/ # Main Django app
│ ├── views.py # AI + ML logic
│ ├── models.py # Trip, Itinerary, Recommendation
│ ├── forms.py # Custom forms
│ ├── urls.py
│ └── templates/
├── ml/ # ML model & encoder
│ ├── recommendation_model.pkl
│ └── bud_encoder.pkl
├── data/
│ └── worldwide_travel_cities.csv
├── static/
├── manage.py
└── requirements.txt

---



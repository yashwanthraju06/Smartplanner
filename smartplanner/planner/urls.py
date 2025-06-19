from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('plan/', views.plan_trip, name='plan_trip'),
    path('itinerary/<int:trip_id>/', views.view_itinerary, name='view_itinerary'),
    path('recommend/', views.recommend_destinations, name='destination_recommendation'),
    path('history/', views.recommendation_history, name='recommendation_history'),
]

from django.db import models
from django.contrib.auth.models import User

# User Profile Model (Optional, for extra info)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

# Main Trip model
class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    interests = models.TextField(help_text="Comma-separated interests (e.g., adventure, culture)")
    budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Your maximum budget in ₹")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.destination}"

# Budget model (AI-estimated cost, optional)
class Budget(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='budget_info')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Budget for {self.trip.destination}: ₹{self.estimated_cost}"

class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()

    def __str__(self):
        return self.key

class Itinerary(models.Model):
    trip = models.OneToOneField('Trip', on_delete=models.CASCADE)
    details = models.TextField()

    def __str__(self):
        return f"Itinerary for {self.trip.destination} ({self.trip.user.username})"


class RecommendationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.PositiveIntegerField()
    interests = models.TextField()
    recommended_cities = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.user.username} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
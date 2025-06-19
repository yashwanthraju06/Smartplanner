from django.contrib import admin
from .models import Profile, Trip, Itinerary, Budget, AppSetting, RecommendationLog
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Inline profile when viewing User in admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

# Extend default User admin to include Profile
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# Unregister original User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("user", "destination", "start_date", "end_date", "created_at")
    search_fields = ("destination", "user__username")

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ("trip",)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("trip", "estimated_cost")

admin.site.register(AppSetting)

admin.site.register(RecommendationLog)

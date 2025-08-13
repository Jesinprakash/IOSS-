from django.contrib import admin
from .models import Url

@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display = ("short_code", "original_url", "clicks", "created_at", "is_active")
    search_fields = ("short_code", "original_url")
    list_filter = ("is_active", "created_at")

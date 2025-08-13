from django.urls import path
from . import views

app_name = "links"

from django.urls import path
from . import views

app_name = "links"  # important so reverse() works with 'links:qr_code'

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("detail/<str:code>/", views.DetailView.as_view(), name="detail"),
    path("<str:code>/", views.follow, name="follow"),
    path("qr/<str:code>/", views.qr_code, name="qr_code"),  # <-- Add this
]


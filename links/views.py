from django.shortcuts import render

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.db import transaction
from django.core.cache import cache
import io
import qrcode


from .forms import UrlForm
from .models import Url
from .utils import generate_unique_code

RATE_WINDOW_SECONDS = 600  # 10 minutes


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


class HomeView(View):
    template_name = "links/home.html"

    def get(self, request):
        form = UrlForm()
        session_key = request.session.session_key or request.session.save()
        my_links = Url.objects.filter(owner_session=request.session.session_key).order_by("-created_at")[:10]
        return render(request, self.template_name, {"form": form, "links": my_links, "base": settings.BASE_APP_URL})

    def post(self, request):
        # simple IP-based rate limit for create
        ip = _client_ip(request)
        key = f"rate:{ip}"
        count = cache.get(key, 0)
        if count >= settings.CREATE_RATE_LIMIT:
            form = UrlForm(request.POST)
            return render(request, self.template_name, {
                "form": form,
                "error": "Too many creations, please wait a few minutes.",
                "links": Url.objects.filter(owner_session=request.session.session_key).order_by("-created_at")[:10],
                "base": settings.BASE_APP_URL,
            }, status=429)
        cache.set(key, count + 1, timeout=RATE_WINDOW_SECONDS)

        form = UrlForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "links": [], "base": settings.BASE_APP_URL})

        original = form.cleaned_data["original_url"]
        with transaction.atomic():
            code = generate_unique_code()
            if not request.session.session_key:
                request.session.save()
            u = Url.objects.create(original_url=original, short_code=code, owner_session=request.session.session_key)
        short_link = f"{settings.BASE_APP_URL}/{u.short_code}"
        return HttpResponseRedirect(reverse("links:detail", args=[u.short_code]))


class DetailView(View):
    template_name = "links/detail.html"

    def get(self, request, code):
        try:
            u = Url.objects.get(short_code=code, is_active=True)
        except Url.DoesNotExist:
            raise Http404
        short_link = f"{settings.BASE_APP_URL}/{u.short_code}"
        return render(request, self.template_name, {"u": u, "short_link": short_link})


def follow(request, code):
    try:
        u = Url.objects.get(short_code=code, is_active=True)
    except Url.DoesNotExist:
        return render(request, "links/not_found.html", {"code": code}, status=404)

    u.clicks = (u.clicks or 0) + 1
    u.last_accessed = timezone.now()
    u.save(update_fields=["clicks", "last_accessed"])
    return HttpResponseRedirect(u.original_url)


def qr_code(request, code):
    try:
        u = Url.objects.get(short_code=code, is_active=True)
    except Url.DoesNotExist:
        raise Http404
    img = qrcode.make(f"{settings.BASE_APP_URL}/{u.short_code}")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")

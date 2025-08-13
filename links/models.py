from django.db import models

from django.db import models
from django.utils import timezone

class Url(models.Model):
    original_url = models.URLField(max_length=2048)
    short_code = models.SlugField(max_length=32, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    clicks = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    owner_session = models.CharField(max_length=64, db_index=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.short_code} → {self.original_url}"

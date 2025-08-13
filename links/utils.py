import random
import string
from django.conf import settings
from .models import Url

ALPHABET = string.ascii_letters + string.digits


def generate_unique_code(length: int | None = None) -> str:
    length = length or settings.SHORT_CODE_LENGTH
    while True:
        code = "".join(random.choices(ALPHABET, k=length))
        if not Url.objects.filter(short_code=code).exists():
            return code
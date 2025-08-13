from django import forms

class UrlForm(forms.Form):
    original_url = forms.URLField(
        label="Long URL",
        widget=forms.URLInput(attrs={
            "class": "w-full rounded-xl border p-3",
            "placeholder": "https://example.com/very/long/url",
        }),
    )
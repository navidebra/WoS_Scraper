from django import forms


class ScraperForm(forms.Form):
    country = forms.CharField(label='Country', max_length=100)

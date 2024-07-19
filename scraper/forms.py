from django import forms


class ScraperForm(forms.Form):
    directory = forms.CharField(label='Directory', max_length=255)
    country = forms.CharField(label='Country', max_length=100)

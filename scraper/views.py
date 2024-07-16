import os
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ScraperForm
from . import wos_scraper


def index(request):
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            directory = form.cleaned_data['directory']
            country = form.cleaned_data['country']

            # Check if the directory exists, if not, create it
            if not os.path.exists(directory):
                os.makedirs(directory)

            wos_scraper.Scraper(directory, country)
            return HttpResponse(f'Scraping completed. Files saved in {directory}.')
    else:
        form = ScraperForm()

    return render(request, 'index.html', {'form': form})

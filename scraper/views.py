import os
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
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

            df_results, df_errors = wos_scraper.Scraper(directory, country)

            # Save dataframes to CSV files
            results_file = os.path.join(directory, 'results.csv')
            errors_file = os.path.join(directory, 'errors.csv')
            df_results.to_csv(results_file, index=False)
            df_errors.to_csv(errors_file, index=False)

            # Provide links to download the files
            response_content = (
                f'Scraping completed. Files saved in {directory}.<br>'
                f'<a href="/download/?file={results_file}">Download Results</a><br>'
                f'<a href="/download/?file={errors_file}">Download Errors</a>'
            )
            return HttpResponse(response_content)
    else:
        form = ScraperForm()

    return render(request, 'index.html', {'form': form})

def download(request):
    file_path = request.GET.get('file')
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        return response
    else:
        return HttpResponse('File not found.')
import os
import tempfile
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from .forms import ScraperForm
from . import wos_scraper


def index(request):
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']

            # Use a temporary directory to save files
            with tempfile.TemporaryDirectory() as temp_dir:
                wos_scraper.Scraper(temp_dir, country)

                results_file = 'results.csv'
                errors_file = 'errors.csv'

                # Prepare files for download
                with open(results_file, 'rb') as rf, open(errors_file, 'rb') as ef:
                    response = HttpResponse(content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename={country}_scrape_results.zip'

                    import zipfile
                    import io

                    buffer = io.BytesIO()
                    with zipfile.ZipFile(buffer, 'w') as zf:
                        zf.writestr('results.csv', rf.read())
                        zf.writestr('errors.csv', ef.read())

                    buffer.seek(0)
                    response.write(buffer.read())
                    return response
    else:
        form = ScraperForm()

    return render(request, 'index.html', {'form': form})

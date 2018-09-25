import os

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render


# Create your views here.

def get_file_names(directory):
    """Returns list of file names within directory"""
    contents = os.listdir(directory)
    files = list()
    for item in contents:
        if os.path.isfile(os.path.join(directory, item)):
            files.append(item)
    return files


def report_list(request):
    """default view - listing of the directory"""
    data = {
        'directory_name': os.path.basename(settings.REPORT_DAILYSTUDY_DIRECTORY),
        'directory_files': get_file_names(settings.REPORT_DAILYSTUDY_DIRECTORY)
    }
    template = 'reports/list.html'
    return render(request, template, data)


def report_download(request, report_name):
    file_path = settings.REPORT_DAILYSTUDY_DIRECTORY + report_name
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

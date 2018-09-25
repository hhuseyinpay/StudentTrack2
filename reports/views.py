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


report_directory = settings.MEDIA_ROOT + '/reports/excel/daily_study/'


def report_list(request):
    """default view - listing of the directory"""
    data = {
        'directory_name': os.path.basename(report_directory),
        'directory_files': get_file_names(report_directory)
    }
    template = getattr(settings, 'DIRECTORY_TEMPLATE', 'reports/list.html')
    return render(request, template, data)


def report_download(request, report_name):
    file_path = report_directory + report_name
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

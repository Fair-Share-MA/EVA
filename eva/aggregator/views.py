import re
from click import edit
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import FileFieldForm

# Create your views here.
def home_screen(request):
    if request.method == "POST":
        form = FileFieldForm(request.POST, request.FILES)
        files = request.FILES.getlist('file_field')
        for f in files:
            print(str(f))
        return HttpResponse(str(files))
    else:
        form = FileFieldForm()

    return render(request, 'aggregator/home.html', {
        "form": form
    })
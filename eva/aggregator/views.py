from django.shortcuts import render
from .forms import FileFieldForm
from django.core.files.storage import FileSystemStorage
from .scripts.eva_cli import eva_main
import json

# Create your views here.
def home_screen(request):
    export_file_url = None
    processing = False

    if request.method == "POST":
        processing = True
        form = FileFieldForm(request.POST, request.FILES)
        files = request.FILES.getlist('file_field')
        overrides = json.loads(request.POST.get('overrides'))

        fs = FileSystemStorage()
        upload_save_fnames = []
        for file in files:
            name = fs.save(file.name, file)
            upload_save_fnames.append(name)

        export_file_url = fs.url(eva_main(upload_save_fnames, overrides))
        processing = False
    else:
        form = FileFieldForm()

    return render(request, 'aggregator/home.html', {
        "form": form,
        "export_result": export_file_url,
        "processing": processing
    })
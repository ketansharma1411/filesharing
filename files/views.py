# Create your views here.
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from .models import FileUpload
from .forms import FileUploadForm
from django.contrib import messages

import uuid
# def upload_file(request):
#     print('hello')
#     if request.method == 'POST' and request.FILES:
#         print('post request')
#         form = FileUploadForm(request.POST, request.FILES)
#         project_name=request.POST.get('project_name')
#         print(request.FILES)
#         print(form.is_valid())
#         if form.is_valid():
#             print('into the form')
            
#             file_id=uuid.uuid4()
#             files = request.FILES.getlist('file')  # Get the list of files uploaded
            
#             # Loop through each uploaded file and create a FileUpload object
#             for file in files:
#                 FileUpload.objects.create(file_id=file_id, file=file,project_name=project_name)

#             return render(request, 'upload_success.html', {'file_id': file_id})
#     else:
#         form = FileUploadForm()

#     return render(request, 'upload.html', {'form': form})


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        project_name=request.POST.get('project_name')
        if form.is_valid():
            file_id = str(uuid.uuid4())  # Generate a unique file ID
            files = request.FILES.getlist('file')  # Handle multiple files

            for file in files:
                FileUpload.objects.create(file_id=file_id, file=file,project_name=project_name)

            # Return JSON response with success and redirect URL
            return JsonResponse({'success': True, 'redirect_url': '/upload_success/{}'.format(file_id)})

        else:
            # Return JSON response with error
            return JsonResponse({'success': False, 'error': 'Invalid form submission.'})
    else:
        form = FileUploadForm()

    return render(request, 'upload.html', {'form': form})

def display_files(request):
    if request.method == 'POST':
        # Get the file_id entered by the user
        file_id = request.POST.get('file_id')

        # Fetch all files associated with the file_id
        # print(type(file_id))
        # file_id=uuid.UUID(file_id)
        # if type(file_id)!=uuid.UUID:
        #     messages.error(request, 'No files found with this ID. Please enter Valid ID.')
        #     return render(request, 'download_file.html')
        files = FileUpload.objects.filter(file_id=file_id)
        
        if not files.exists():
            # If no files are found with the entered ID, show an error message
            messages.error(request, 'No files found with this ID. Please check and try again.')
            return render(request, 'download_file.html')
        
        # Render the page with the list of files
        return render(request, 'download_file.html', {'files': files, 'file_id': file_id})

    # If GET request, just render the empty form
    return render(request, 'download_file.html')

def download_file(request, file_id,ID):
    # Get the file object for the given file_id
    file_to_download = get_object_or_404(FileUpload, file_id=file_id,id=ID)
    # print(file_to_download,'jhsdfj')

    # Create an HTTP response with the file content
    response = HttpResponse(file_to_download.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="fileshare/{file_to_download.file.name}"'
    
    return response

def about(request):
    return render(request, 'about.html')
def upload_success(request,file_id):
    return render(request, 'upload_success.html', {'file_id': file_id})

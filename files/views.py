# Create your views here.
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from .models import FileUpload
from .forms import FileUploadForm
from django.contrib import messages

import boto3
from decouple import config
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import uuid

from django.core.files.storage import default_storage
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        project_name=request.POST.get('project_name')
        if form.is_valid():
            file_id = str(uuid.uuid4())  # Generate a unique file ID
            files = request.FILES.getlist('file')  # Handle multiple files

            for file in files:
                # This is to directly upload the file in s3 bucket
                # file_name = f'uploads/{file.name}'  
                # file_path = default_storage.save(file_name, file)  
                # file_url = default_storage.url(file_path)  

                # Create a record in the database with the file path (URL)
                FileUpload.objects.create(
                    file_id=file_id,
                    file=file,
                    project_name=project_name
                )



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
        files = FileUpload.objects.filter(file_id=file_id)
        
        if not files.exists():
            # If no files are found with the entered ID, show an error message
            messages.error(request, 'No files found with this ID. Please check and try again.')
            return render(request, 'download_file.html')
        
        # Render the page with the list of files
        return render(request, 'download_file.html', {'files': files, 'file_id': file_id})

    # If GET request, just render the empty form
    return render(request, 'download_file.html')

# from django.http import HttpResponseRedirect
# def download_file(request, file_id,ID):

#     # file_to_download = get_object_or_404(FileUpload, file_id=file_id,id=ID)
#     # response = HttpResponse(file_to_download.file, content_type='application/octet-stream')
#     # response['Content-Disposition'] = f'attachment; filename="fileshare/{file_to_download.file.name}"'
#     # return response

#      # Get the file object for the given file_id
#     file_to_download = get_object_or_404(FileUpload, file_id=file_id, id=ID)
    
#     # Generate a presigned URL for downloading the file from S3
#     file_url = file_to_download.file.url
#     print(file_url)

#     # Redirect the user to the S3 URL for downloading
#     return HttpResponseRedirect(file_url)




def download_file(request, file_id, ID):
    # Get the file object for the given file_id and ID
    file_to_download = get_object_or_404(FileUpload, file_id=file_id, id=ID)
    
    # Get the S3 URL of the file
    file_url = file_to_download.file.url
    print(file_url)

    # return HttpResponseRedirect(file_url)
    
    # Extract the bucket name and file key from the URL (assuming the URL format is standard)
    bucket_name = config('AWS_STORAGE_BUCKET_NAME')
    file_key = file_to_download.file.name  # The file path in your S3 bucket

    # Create an S3 client
    s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name= config('AWS_S3_REGION_NAME')
        )

    # Try to fetch the file from S3 and stream it
    try:
        # S3 has a method to get the file as a stream
        s3_object = s3.get_object(Bucket=bucket_name, Key=file_key)

        # The file content will be streamed directly to the client
        file_stream = s3_object['Body']

        # Create a StreamingHttpResponse with the file stream and the appropriate headers
        response = StreamingHttpResponse(file_stream, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_to_download.file.name}"'
        return response
    except (NoCredentialsError, PartialCredentialsError):
        return HttpResponse("Error: AWS credentials are missing or invalid.", status=400)
    except Exception as e:
        return HttpResponse(f"Error downloading file: {str(e)}", status=500)

def about(request):
    return render(request, 'about.html')
def upload_success(request,file_id):
    return render(request, 'upload_success.html', {'file_id': file_id})

# This is to test S3 bucket upload test
def testing(request):
    s3 = boto3.client(
        's3',
        aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
        region_name= config('AWS_S3_REGION_NAME')
    )

    # Test upload
    try:
        s3.upload_file('D:/django-fileshare/fileshare/files/test.txt', 'fileshare2003', 'uploads/test.txt')
        print("File uploaded successfully!")
        return HttpResponse("File uploaded successfully!")
    except Exception as e:
        print("Error:", e)
        return HttpResponse(f"Error: {e}", status=500)

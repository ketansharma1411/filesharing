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
from storages.backends.s3boto3 import S3Boto3Storage
from urllib.parse import quote,unquote
from urllib.parse import urlparse
import zipfile
import io

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        project_name=request.POST.get('project_name')

        # make project name safe
        temp_name=project_name.split(' ')
        project_name='_'.join(temp_name)
        
        if form.is_valid():
            file_id = str(uuid.uuid4())  # Generate a unique file ID
            files = request.FILES.getlist('file')  # Handle multiple files
            if len(files)==0:
                return JsonResponse({'success': False, 'error': 'Please choose at least one file or folder before submitting.'})



            s3_storage = S3Boto3Storage()  # Create an instance of S3 storage
            total_size = sum(file.size for file in files)

            if total_size>200 * 1024 * 1024 and len(files)>1:
                # Create a ZIP file in memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file in files:
                        # Add each file to the zip
                        zip_file.writestr(file.name, file.read())

                
                zip_file_name = f'uploads/{project_name}/{file_id}/{project_name}.zip'  # Define the S3 path
                zip_buffer.seek(0)  # Seek to the beginning of the buffer before uploading

                # Save the ZIP file to S3
                folder_path=s3_storage.save(zip_file_name, zip_buffer)
                file_url = s3_storage.url(folder_path)  

                # Create a record in the database with the ZIP file URL
                FileUpload.objects.create(
                    file_id=file_id,
                    file=None,  # No actual file, we have a zip URL instead
                    project_name=project_name,
                    file_url=file_url  # Store the URL of the uploaded ZIP file
                )
            else:
                for file in files:

                    # This is to directly upload the file in s3 bucket

                    file_name = f'uploads/{project_name}/{file_id}/{file.name}'  
                    # file_path = default_storage.save(file_name, file)  
                    # file_url = default_storage.url(file_path) 
                    # print("file url to s3 bucket",file_url) 
                    file_path = s3_storage.save(file_name, file)  
                    file_url = s3_storage.url(file_path)  # Get the S3 URL

                    # Create a record in the database with the file path (URL)
                    FileUpload.objects.create(
                        file_id=file_id,
                        file=file,
                        project_name=project_name,
                        file_url=file_url
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


def download_file(request, file_id, ID):
    # Get the file object for the given file_id and ID
    file_to_download = get_object_or_404(FileUpload, file_id=file_id, id=ID)
    
    # Get the S3 URL of the file from the database (already saved)
    file_url = file_to_download.file_url
    
    # Extract bucket name and file key from the URL (excluding query params)
    parsed_url = urlparse(file_url)
    file_key = parsed_url.path.lstrip('/')  # Remove leading '/' from path to get file key
    file_key=unquote(file_key)  # Decode the URL-encoded file key
    # print('this is the file_key',file_key)


    # Create an S3 client (use the same S3 credentials)
    s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_S3_REGION_NAME')
        )

    # Extract bucket name and file key from the URL
    bucket_name = config('AWS_STORAGE_BUCKET_NAME')


    # Try to fetch the file from S3 and stream it
    try:
        # S3 has a method to get the file as a stream
        s3_object = s3.get_object(Bucket=bucket_name, Key=file_key)

        # The file content will be streamed directly to the client
        file_stream = s3_object['Body']

        # Create a StreamingHttpResponse with the file stream and appropriate headers
        response = StreamingHttpResponse(file_stream, content_type='application/octet-stream')
        download_file_name=file_to_download.file.name
        if download_file_name is None or download_file_name == '' or file_to_download.file is None:
            download_file_name='fileshare_file.zip'
        print('this is the download_file_name',download_file_name)
        response['Content-Disposition'] = f'attachment; filename="{download_file_name}"'
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

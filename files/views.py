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
import qrcode
from io import BytesIO
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings
import base64
import threading

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

            # if sum(file.size for file in files)>950 * 1024 * 1024:
            #     return JsonResponse({'success': False, 'error': 'File size exceeds the maximum limit of 1GB.'})


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

    return render(request, 'upload_page_v2.html', {'form': form})

def display_files(request):
    if request.method == 'POST':
        # Get the file_id entered by the user
        file_id = request.POST.get('file_id')
        files = FileUpload.objects.filter(file_id=file_id)
        
        if not files.exists():
            # If no files are found with the entered ID, show an error message
            messages.error(request, 'No files found with this ID. Please check and try again.')
            return render(request, 'download_page_v2.html')
        
        # Render the page with the list of files
        return render(request, 'download_page_v2.html', {'files': files, 'file_id': file_id})
    
    file_id=request.GET.get('key') or None
    if file_id:
        files = FileUpload.objects.filter(file_id=file_id)
        return render(request, 'download_page_v2.html', {'files': files, 'file_id': file_id})
    
    # If GET request, just render the empty form
    return render(request, 'download_page_v2.html')


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
    return render(request, 'home_page_v2.html')


def generate_qr_code(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)  # Reset buffer position
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')  # Encode properly
    return qr_code_base64


def upload_success(request,file_id):
    file_url = f"https://filezap.duckdns.org/display/?key={file_id}"
    qr_code_data = generate_qr_code(file_url)
    # print("hello",qr_code_data)
    return render(request, 'upload_success_page_v2.html', {'file_id': file_id,'qr_code_data': qr_code_data})



# gmail sending utility
def send_user_email(user_email, subject, message):
    """Send an email to the user."""
    def send_email():
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # Sender
                [user_email],  # Receiver
                fail_silently=False,
            )
            # print('TRUE the email has been sent successfully!!')
            # return True
        except Exception as e:
            print(f"Error sending email: {e}")
            # return False
    # Run the send_email function in a new thread
    email_thread = threading.Thread(target=send_email)
    email_thread.start()
    return True


def email_send(request):
    user_email = request.GET.get('message')  # Get user email
    key= request.GET.get('key') 
    subject = "Your File is Uploaded!"
    # message = f"Your file has been successfully uploaded. You can download it using this ID: {key}"
    file_url = f"https://filezap.duckdns.org/display/?key={key}"
    message = f"""
    Dear User,

    Your file has been successfully uploaded. Here are the details:

    📂 File ID: {key}
    🔗 Download Link: {file_url}

    You can use the file ID to retrieve your file anytime.

    Best Regards,
    Your File Sharing Team
    """


    # Send email
    send_user_email(user_email, subject, message)
    return redirect('about')
    # return HttpResponse("Email sent successfully!")


# FOR MESSAGING
def send_sms_twilio(to_phone_number, message_body):
    # Your Twilio account SID and Auth Token
    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILLO_AUTH_TOKEN')
    
    # Initialize the Twilio client
    client = Client(account_sid, auth_token)
    
    # Send the message
    message = client.messages.create(
        body=message_body,          # The content of the message
        from_='+12767884701',         # Your Twilio phone number (provided by Twilio)
        to=to_phone_number          # The recipient's phone number
    )

    # Print message SID (optional)
    print(f"Message sent successfully! SID: {message.sid}")

def send_sms(request):
    phone_number=request.GET.get('message')
    if phone_number.startswith('0'):
        phone_number = phone_number[1:]
    elif phone_number.startswith('+91'):
        phone_number = phone_number[3:]
    elif phone_number.startswith('91'):
        phone_number = phone_number[2:]
    
    phone_number = '+91' + phone_number
    key= request.GET.get('key') 
    message = (
        f"Dear User,\n\n"
        f"We are pleased to inform you that your requested file is ready for download. "
        f"Please use the following unique file ID to access and download your file:\n\n"
        f"File ID: {key}\n\n"
        f"To download the file, visit the link below:\n"
        f"https://filezap.duckdns.org/display/?key={key}\n\n"
        f"Thank you for using our service. If you have any questions, feel free to contact us.\n\n"
        f"Best regards,\n"
        f"FileZap"
    )
    try:
        send_sms_twilio(phone_number, message)
        return redirect('about')
        # return HttpResponse("SMS sent successfully!")
    except Exception as e:
        return redirect('about')
        # return HttpResponse(f"SMS sent failure!{e}", status=500)


def community(request):
    return render(request, 'community_page_v2.html')

def privacy(request):
    return render(request, 'privacy_page_v2.html')

def termsCondition(r):
    return render(r, 'terms_condition_page_v2.html')

def testing_design(r):
    return render(r, 'upload_success_page_v2.html')


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





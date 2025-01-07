from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    # path('download/', views.download_file, name='download_file'),
    path('about/',views.about,name='about'),
    path('display/', views.display_files, name='display_files'),  # Display all files
    path('download/<uuid:file_id>/<int:ID>', views.download_file, name='download_file'),  # Download specific file
    path('upload_success/<uuid:file_id>', views.upload_success, name='upload_success'),

]
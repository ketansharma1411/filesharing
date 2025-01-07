from django.contrib import admin
from .models import FileUpload

# Register your models here.
# admin.site.register(FileUpload)

class FileUploadAdmin(admin.ModelAdmin):
    # Add 'id' to the list_display to show it in the admin list view
    list_display = ('id', 'project_name', 'file', 'uploaded_at')

admin.site.register(FileUpload, FileUploadAdmin)
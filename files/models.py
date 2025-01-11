import uuid
from django.db import models

class FileUpload(models.Model):
    # id = models.AutoField(primary_key=True)
    file_id = models.CharField(max_length=150,default=str(uuid.uuid4),unique=False)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    project_name=models.CharField(max_length=200,null=True,blank=True)
    file_url=models.CharField(max_length=450,blank=True,null=True)

    def __str__(self):
        return f"{self.project_name}"
from django import forms
from .models import FileUpload

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['file']
    # file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)


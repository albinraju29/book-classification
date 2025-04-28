from django.db import models
from django.utils import timezone

class BookPrediction(models.Model):
    # File name (PDF, Image, etc.)
    file_name = models.CharField(max_length=255)
    
    # File type extension (like JPG, PNG, PDF, etc.)
    file_type = models.CharField(max_length=50, blank=True)
    
    # If images are used, store image separately
    image_file = models.ImageField(upload_to='', blank=True, null=True)
    
    # Time of upload
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    # Your prediction fields
    predicted_genre = models.CharField(max_length=100)
    extracted_text = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.file_name} - {self.predicted_genre}"

    # Optional: Get file extension if you want to use in templates
    @property
    def file_extension(self):
        if self.file_name:
            return self.file_name.split('.')[-1].upper()
        return "UNKNOWN"

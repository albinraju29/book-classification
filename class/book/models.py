from django.db import models
from django.contrib.auth.models import User

class BookPrediction(models.Model):
    # Simplified version for college project
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    genre = models.CharField(max_length=100)
    extracted_text = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.file_name} - {self.genre}"
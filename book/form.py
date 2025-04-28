from django import forms
from .models import Book

class BookUploadForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'description', 'cover_image', 'text_file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get('description')
        cover_image = cleaned_data.get('cover_image')
        text_file = cleaned_data.get('text_file')
        
        if not description and not cover_image and not text_file:
            raise forms.ValidationError("You must provide either a description, cover image, or text file.")
        
        return cleaned_data
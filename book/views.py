from django.shortcuts import get_object_or_404, render, redirect
from django.core.files.storage import FileSystemStorage
import numpy as np
from .models import BookPrediction
from django.conf import settings
import os
import joblib
import pickle
import easyocr
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Initialize NLP components once
nltk.download('punkt')
nltk.download('stopwords')
reader = easyocr.Reader(['en'])

# Load ML models
try:
    model = joblib.load(os.path.join(settings.BASE_DIR, 'book', 'model_files', 'genre_prediction_model.pkl'))
    vectorizer = joblib.load(os.path.join(settings.BASE_DIR, 'book', 'model_files', 'tfidf_vectorizer.pkl'))
    with open(os.path.join(settings.BASE_DIR, 'book', 'model_files', 'genre_label_encoder.pkl'), 'rb') as f:
        encoder = pickle.load(f)
    with open(os.path.join(settings.BASE_DIR, 'book', 'model_files', 'genre_mapping.pkl'), 'rb') as f:
        genre_mapping = pickle.load(f)
    print("Models loaded successfully")
except Exception as e:
    raise RuntimeError(f"Failed to load ML models: {str(e)}")

def home(request):
    recent_predictions = BookPrediction.objects.all().order_by('-id')[:5]
    return render(request, 'home.html', {'recent_predictions': recent_predictions})

def predict(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            print("Starting prediction process...")

            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()

            # Step 1: Validate file size
            if uploaded_file.size > 5 * 1024 * 1024:
                print("File too large.")
                return render(request, 'home.html', {'error': "File size exceeds 5MB limit."})
            print("✅ File received:", uploaded_file.name)

            # Step 2: Save file
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()  # Extract file extension
            print("✅ File saved at:", file_path)

            # Step 3: Extract text
            results = reader.readtext(file_path, detail=0)
            extracted_text = " ".join(results)
            print("✅ Text extracted:", extracted_text[:100] + "...")  # Show first 100 chars

            # Step 4: Get description
            description = request.POST.get('description', '')
            print("✅ Description received:", description[:100] + "...")

            combined_text = f"{extracted_text} {description}".strip()

            # Step 5: Preprocess text
            stop_words = set(stopwords.words('english'))
            words = word_tokenize(combined_text.lower())
            cleaned_text = " ".join(
                [re.sub(r'\W', '', word) for word in words if word not in stop_words and word.isalpha()]
            )
            print("✅ Cleaned text:", cleaned_text[:100] + "...")

            # Step 6: Vectorize text
            text_vector = vectorizer.transform([cleaned_text])
            print("✅ Text vectorized")

            # Step 7: Predict
            prediction = model.predict(text_vector)
            print("✅ Raw prediction:", prediction)

            # Step 8: Get the predicted genre ID
            predicted_genre_id = prediction[0]
            print("✅ Predicted genre ID:", predicted_genre_id)

            # Step 9: Get the genre name from the mapping
            # First, check if we need to use encoder or direct mapping
            if isinstance(genre_mapping, dict):
                # If genre_mapping is {genre_name: id}, we need to reverse it
                reversed_mapping = {v: k for k, v in genre_mapping.items()}
                predicted_genre = reversed_mapping.get(predicted_genre_id, "Unknown Genre")
            else:
                # If genre_mapping is a list or array where index corresponds to genre
                try:
                    predicted_genre = genre_mapping[predicted_genre_id]
                except (IndexError, KeyError):
                    predicted_genre = "Unknown Genre"
            
            print("✅ Final predicted genre:", predicted_genre)

            # Step 10: Save to database
            prediction = BookPrediction.objects.create(
                file_name=filename,
                file_type=file_extension,
                image_file=filename if uploaded_file.content_type.startswith('image') else None,
                extracted_text=extracted_text,
                predicted_genre=predicted_genre,
                description=description  # Add this if you want to store the description
            )
            print("✅ Prediction saved to database")

            request.session['prediction_id'] = prediction.id
            return redirect('processing')
        
        except Exception as e:
            print("❌ Error during prediction:", str(e))
            request.session['prediction_error'] = str(e)
            return redirect('error')
    else:
        print("No file uploaded in request.")
        return render(request, 'home.html', {'error': "Please upload a valid book cover image."})


def processing(request):
    # Check if prediction_id exists in session
    if 'prediction_id' not in request.session:
        return redirect('home')
    return render(request, 'processing.html')

def result(request):
    # Get prediction ID from session
    prediction_id = request.session.get('prediction_id')
    
    if not prediction_id:
        return redirect('home')
    
    # Get the prediction object
    prediction = get_object_or_404(BookPrediction, id=prediction_id)
    
    # Clear the session
    if 'prediction_id' in request.session:
        del request.session['prediction_id']
    
    return render(request, 'result.html', {
        'prediction': prediction,
        'predicted_genre': prediction.predicted_genre,
        'extracted_text': prediction.extracted_text,
        'filename': prediction.file_name,
        'filetype': prediction.file_type,
        'uploaded_at': prediction.uploaded_at
    })

def recent_predictions(request):
    recent_predictions = BookPrediction.objects.all().order_by('-uploaded_at')[:10]  # Show last 10 predictions
    return render(request, 'recent_predictions.html', {'recent_predictions': recent_predictions})

def prediction_detail(request, prediction_id):
    prediction = get_object_or_404(BookPrediction, id=prediction_id)
    return render(request, 'prediction_detail.html', {'prediction': prediction})

def error(request):
    error_message = request.session.get('prediction_error', 'An unknown error occurred')
    if 'prediction_error' in request.session:
        del request.session['prediction_error']
    
    return render(request, 'error.html', {
        'error': error_message,
        'exception': error_message if settings.DEBUG else None
    })
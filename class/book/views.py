from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
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
except Exception as e:
    raise RuntimeError(f"Failed to load ML models: {str(e)}")

def home(request):
    recent_predictions = BookPrediction.objects.all().order_by('-id')[:5]
    return render(request, 'home.html', {'recent_predictions': recent_predictions})

def predict(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()

            # Validate file size (max 5MB)
            if uploaded_file.size > 5 * 1024 * 1024:
                return render(request, 'home.html', {'error': "File size exceeds 5MB limit."})

            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            # Extract text from image
            results = reader.readtext(file_path, detail=0)
            extracted_text = " ".join(results)

            # Get optional description
            description = request.POST.get('description', '')
            combined_text = f"{extracted_text} {description}".strip()

            # Clean and preprocess text
            stop_words = set(stopwords.words('english'))
            words = word_tokenize(combined_text.lower())
            cleaned_text = " ".join([re.sub(r'\W', '', word) for word in words if word not in stop_words and word.isalpha()])

            # Vectorize
            text_vector = vectorizer.transform([cleaned_text])

            # Predict
            prediction = model.predict(text_vector)
            predicted_genre = encoder.inverse_transform(prediction)[0]
            genre_display = genre_mapping.get(predicted_genre, predicted_genre)

            # Save to database
            BookPrediction.objects.create(
                filename=uploaded_file.name,
                extracted_text=extracted_text,
                predicted_genre=genre_display
            )

            # Pass data to process page
            context = {
                'filename': uploaded_file.name,
                'extracted_text': extracted_text,
                'predicted_genre': genre_display
            }
            request.session['result_context'] = context  # Save to session for result page
            return render(request, 'processing.html', context)

        except Exception as e:
            return render(request, 'home.html', {'error': str(e)})

    return redirect('home')


def processing(request):
    # Check if we have prediction data
    if 'prediction_results' not in request.session:
        return redirect('home')
        
    # This view shows the processing page
    # JavaScript in the template handles the redirect to result
    return render(request, 'processing.html')


def result(request):
    # Retrieve data from session
    context = request.session.get('result_context', {})
    if not context:
        return redirect('home')
    return render(request, 'result.html', context)

def error(request):
    error_message = request.session.get('prediction_error', 'An unknown error occurred')
    if 'prediction_error' in request.session:
        del request.session['prediction_error']
    
    return render(request, 'error.html', {
        'error': error_message,
        'exception': error_message if settings.DEBUG else None
    })
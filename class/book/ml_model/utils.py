import os
import joblib
import pickle
import easyocr
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.conf import settings

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize EasyOCR reader (do this once)
reader = easyocr.Reader(['en'])

class GenrePredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.encoder = None
        self.genre_mapping = None
        self.load_models()
    
    def load_models(self):
        """Load all ML model components"""
        model_dir = os.path.join(settings.BASE_DIR, 'book', 'model_files')
        
        self.model = joblib.load(os.path.join(model_dir, 'genre_prediction_model.pkl'))
        self.vectorizer = joblib.load(os.path.join(model_dir, 'tfidf_vectorizer.pkl'))
        
        with open(os.path.join(model_dir, 'genre_label_encoder.pkl'), 'rb') as f:
            self.encoder = pickle.load(f)
        
        # Optional: Load genre mapping if exists
        mapping_path = os.path.join(model_dir, 'genre_mapping.pkl')
        if os.path.exists(mapping_path):
            with open(mapping_path, 'rb') as f:
                self.genre_mapping = pickle.load(f)
    
    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'\W', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        words = word_tokenize(text)
        words = [word for word in words if word not in stopwords.words('english')]
        return ' '.join(words)
    
    def extract_text_from_image(self, image_path):
        results = reader.readtext(image_path, detail=0)
        return " ".join(results)
    
    def predict(self, file_path, description=""):
        # Extract text from image
        image_text = self.extract_text_from_image(file_path)
        
        # Combine with optional description
        combined_text = f"{image_text} {description}"
        
        # Preprocess text
        processed_text = self.preprocess_text(combined_text)
        
        # Vectorize text
        text_tfidf = self.vectorizer.transform([processed_text]).toarray()
        
        # Predict genre
        prediction = self.model.predict(text_tfidf)
        genre = self.encoder.inverse_transform(prediction)[0]
        
        return {
            'genre': genre,
            'extracted_text': image_text,
            'processed_text': processed_text
        }

# Initialize predictor when module is loaded
predictor = GenrePredictor()
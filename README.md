```markdown
 📚 Book Classification System

A Django web application that classifies book genres using machine learning (OCR + text classification).

Input Design
 🌟 Key Features Visualized

![Upload Interface](https://github.com/albinraju29/book-classification/raw/main/i2.PNG)  
*Drag-and-drop or click to upload book covers*

![Analysis Screen](https://github.com/albinraju29/book-classification/raw/main/i2.PNG)  
*Text extraction and classification in progress*

![Prediction Output](https://github.com/albinraju29/book-classification/raw/main/o1.PNG)  
Genre prediction with confidence score

![Text Extraction](https://github.com/albinraju29/book-classification/raw/main/o2.PNG)  
*Raw extracted text from the book cover*


Output Design

https://github.com/albinraju29/book-classification/blob/main/o1.PNG
https://github.com/albinraju29/book-classification/blob/main/o2.PNG


 🌟 Features

- **Image Processing**: Extracts text from book covers using EasyOCR
- **Text Classification**: Predicts genre from extracted text with 79% accuracy
- **Django Interface**: User-friendly web interface for uploads and predictions
- **Database Tracking**: Stores all prediction history
- **11 Genres Supported**: Fiction, History, Science, Thriller, etc.

 🛠️ Project Structure

```
book_classify/
├── book/                          # Main Django app
│   ├── migrations/                # Database migrations
│   ├── model_files/               # ML model assets
│   │   ├── genre_label_encoder.pkl
│   │   ├── genre_prediction_model.pkl
│   │   └── tfidf_vectorizer.pkl
│   ├── templates/                 # Frontend templates
│   │   ├── base.html
│   │   ├── home.html              # Upload interface
│   │   ├── result.html            # Prediction results
│   │   └── processing.html        # Loading screen
│   ├── models.py                  # Database schema
│   ├── views.py                   # Business logic
│   └── urls.py                    # App routing
├── media/                         # Uploaded files storage
├── book_classify/                 # Project config
│   ├── settings.py                # Django settings
│   └── urls.py                    # Main URLs
└── manage.py                      # Django CLI
```

 🚀 Installation Guide

= Prerequisites
- Python 3.8+
- Tesseract OCR (for local development)
- Virtual environment recommended

 1. Clone Repository
```bash
git clone https://github.com/albinraju29/book-classification.git
cd book-classification
```

 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

 3. Install Dependencies
```bash
pip install -r requirements.txt
```

 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

 5. Create Admin User (Optional)
```bash
python manage.py createsuperuser
```

 6. Run Development Server
```bash
python manage.py runserver
```
Access at: http://localhost:8000

 🔍 How It Works

Machine Learning Pipeline
1. Text Extraction (EasyOCR)
   ```python
   reader = easyocr.Reader(['en'])
   results = reader.readtext(image_path)
   ```

2. Text Preprocessing
   - Lowercasing
   - Stopword removal
   - Special character removal
   ```python
   def preprocess_text(text):
       text = text.lower()
       text = re.sub(r'\W', ' ', text)
       words = word_tokenize(text)
       words = [w for w in words if w not in stopwords.words('english')]
       return ' '.join(words)
   ```

3. Classification
   ```python
   text_vector = vectorizer.transform([cleaned_text])
   prediction = model.predict(text_vector)
   genre = encoder.inverse_transform(prediction)[0]
   ```

 Django Workflow
1. User uploads image via `home.html`
2. System processes image in `views.predict()`
3. Results displayed in `result.html`
4. Prediction stored in database:
   ```python
   class BookPrediction(models.Model):
       file_name = models.CharField(max_length=255)
       predicted_genre = models.CharField(max_length=100)
       extracted_text = models.TextField()
   ```

 🧰 Management Commands

| Command | Purpose |
|---------|---------|
| `python manage.py runserver` | Start development server |
| `python manage.py makemigrations` | Create DB migrations |
| `python manage.py migrate` | Apply migrations |
| `python manage.py collectstatic` | Gather static files |
| `python manage.py createsuperuser` | Create admin account |

 🌐 Deployment Notes

For production deployment:
1. Set `DEBUG = False` in `settings.py`
2. Configure allowed hosts:
   ```python
   ALLOWED_HOSTS = ['yourdomain.com']
   ```
3. Use production WSGI server (Gunicorn/UWSGI)
4. Set up static files with Nginx/Apache

 📊 Model Performance

| Model | Accuracy | Precision | Recall |
|-------|----------|-----------|--------|
| LinearSVC | 79.05% | 0.78 | 0.79 |
| Logistic Regression | 77.8% | 0.77 | 0.78 |
| Naive Bayes | 75.2% | 0.74 | 0.75 |

 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/foo`)
3. Commit changes (`git commit -am 'Add foo'`)
4. Push to branch (`git push origin feature/foo`)
5. Create Pull Request

 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

Note: For detailed ML training code, see [prediction.ipynb](notebooks/prediction.ipynb)
```

Key improvements made:
1. Added detailed installation and setup instructions
2. Included visual project structure breakdown
3. Explained both ML and Django workflows
4. Added management command cheat sheet
5. Included deployment notes
6. Added contribution guidelines
7. Improved formatting for better readability
8. Added placeholder for demo screenshot

Would you like me to add any specific details about:
- The model training process?
- Environment variables configuration?
- Testing instructions?
- API documentation if you decide to expose endpoints?

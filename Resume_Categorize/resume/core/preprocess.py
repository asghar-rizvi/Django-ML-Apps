'''
    Loading model and text vectorizer and preprocessing data,
    and sending predictions to views.py 
'''



import re
import pickle
import logging
from pathlib import Path

# Global Variables
tfidf = None
classifier_model = None

def load_models():
    """Loads TF-IDF vectorizer and classifier model globally."""
    global tfidf, classifier_model  

    PROJECT_ROOT = Path(__file__).parent.parent  

    tfidf_path = PROJECT_ROOT / 'model' / 'tfidf.pkl'
    classifier_path = PROJECT_ROOT / 'model' / 'classifier.pkl'

    try:
        if tfidf_path.exists():
            with open(tfidf_path, 'rb') as f:
                tfidf = pickle.load(f)
            logging.info(f"TF-IDF Model loaded successfully from {tfidf_path}")
        else:
            logging.error(f"TF-IDF Model file not found at {tfidf_path}")
            return
    except Exception as e:
        logging.error(f"An error occurred while loading TF-IDF Model: {e}")
        return

    try:
        if classifier_path.exists():
            with open(classifier_path, 'rb') as f:
                classifier_model = pickle.load(f)
            logging.info(f"Classifier Model loaded successfully from {classifier_path}")
        else:
            logging.error(f"Classifier Model file not found at {classifier_path}")
            return
    except Exception as e:
        logging.error(f"An error occurred while loading Classifier Model: {e}")
        return

def clean_text(text):
    """Preprocesses text by converting to lowercase, removing newlines, and punctuation."""
    text = text.lower()
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r'[^\w\s]', '', text)  

    if tfidf is None:
        logging.error("TF-IDF model not loaded. Cannot transform text.")
        return None
    text = tfidf.transform([text])
    text = text.toarray() if hasattr(text, 'toarray') else text
    return text

def predict_class(txt):

    if classifier_model is None:
        logging.error("Classifier model not loaded. Cannot predict.")
        return None
    
    text_vector = clean_text(txt)
    if text_vector is None:
        return None

    return classifier_model.predict(text_vector)

if __name__ == '__main__':
    load_models()
    
    sample_resume = """ 
    Skills * Programming Languages: JavaScript (React, Node.js, Express.js, jQuery), 
    Python (Flask, Django, FastAPI), Java (Spring Boot, Hibernate), C++, TypeScript. 
    * Web Development: HTML5, CSS3 (SASS, LESS), Bootstrap, Tailwind CSS, Material-UI. 
    * Frameworks & Libraries: React.js, Next.js, Angular, Vue.js, Redux, Zustand, jQuery, Lodash, D3.js.
    * Backend Technologies: Node.js, Express.js, Django, Flask, FastAPI, Spring Boot, REST APIs, GraphQL, WebSockets. 
    * Databases: MySQL, PostgreSQL, MongoDB, Firebase, Redis, Elasticsearch, Cassandra.
    """

    result = predict_class(sample_resume)
    if result is not None:
        print("Predicted Category:", result[0])
    else:
        print("Prediction failed due to missing models.")

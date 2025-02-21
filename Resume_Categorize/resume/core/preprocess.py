'''
    Loading model and text vectorizer and preprocessing data,
    and sending predictions to views.py 
'''

import re
import pickle
import logging
import PyPDF2
from pathlib import Path
import json 
import pandas as pd

# Global Variables
tfidf = None
classifier_model = None
columns_job_placement = None
job_placement_model = None
job_titles = None

def load_models():
    """Loads TF-IDF vectorizer and classifier model globally."""
    global tfidf, classifier_model ,columns_job_placement,job_placement_model, classes_labels_filename, job_titles

    PROJECT_ROOT = Path(__file__).parent.parent  

    tfidf_path = PROJECT_ROOT / 'model' / 'tfidf.pkl'
    classifier_path = PROJECT_ROOT / 'model' / 'classifier.pkl'
    columns_job_placement_path = PROJECT_ROOT / 'class_labels' / 'columns_job.json'
    job_placement_model_path = PROJECT_ROOT / 'model' / 'job_placement.pkl'
    labels_path = PROJECT_ROOT / 'class_labels' / 'label_mapping.json'
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
    
    try:
        if columns_job_placement_path.exists():
            with open(columns_job_placement_path, 'rb') as f:
                columns_job_placement = json.load(f)
            logging.info(f"columns_job_placement_path  loaded successfully from {columns_job_placement_path}")
        else:
            logging.error(f"columns_job_placement_path not found at {columns_job_placement_path}")
            return
    except Exception as e:
        logging.error(f"An error occurred while loading columns_job_placement_path: {e}")
        return
    
    
    try:
        if job_placement_model_path.exists():
            with open(job_placement_model_path, 'rb') as f:
                job_placement_model = pickle.load(f)
            logging.info(f"job_placement_model_path loaded successfully from {job_placement_model_path}")
        else:
            logging.error(f"job_placement_model_path file not found at {job_placement_model_path}")
            return
    except Exception as e:
        logging.error(f"An error occurred while loading job_placement_model_path: {e}")
        return

    try:
        if labels_path.exists():
            with open(labels_path, 'r') as file:
                job_titles = json.load(file)
        else:
            print('file not exist')
    except FileNotFoundError as e:
        logging.error(f"Model loading failed: {e}")


def class_label(num):
    if str(num) in job_titles:
        return job_titles[str(num)]
    else:
        return "Invalid number"

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        extracted_text = page.extract_text()
        if extracted_text: 
            text += extracted_text + '\n'
    return text

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

def predict_placement(features):
    if job_placement_model is None :
        logging.error("Job Placement model not loaded. Cannot predict.")
        return None
    else :
        x = pd.DataFrame(features, columns=columns_job_placement)
        result = job_placement_model.predict(x)
        if result == 0 :
            return 'Not Accepted'
        else:
            return 'Accepted'
    
if __name__ == '__main__':
    load_models()
    
    # sample_resume = """ 
    # Skills * Programming Languages: JavaScript (React, Node.js, Express.js, jQuery), 
    # Python (Flask, Django, FastAPI), Java (Spring Boot, Hibernate), C++, TypeScript. 
    # * Web Development: HTML5, CSS3 (SASS, LESS), Bootstrap, Tailwind CSS, Material-UI. 
    # * Frameworks & Libraries: React.js, Next.js, Angular, Vue.js, Redux, Zustand, jQuery, Lodash, D3.js.
    # * Backend Technologies: Node.js, Express.js, Django, Flask, FastAPI, Spring Boot, REST APIs, GraphQL, WebSockets. 
    # * Databases: MySQL, PostgreSQL, MongoDB, Firebase, Redis, Elasticsearch, Cassandra.
    # """

    # result = predict_class(sample_resume)
    # if result is not None:
    #     print("Predicted Category:", result[0])
    # else:
    #     print("Prediction failed due to missing models.")
    features = [[50,50,50,50,0,0,0,0,0,0,0,0,0,0]]
    print(predict_placement(features))
    

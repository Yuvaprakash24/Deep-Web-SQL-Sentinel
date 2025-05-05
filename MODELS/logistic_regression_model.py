import pickle
import os
import numpy as np
from werkzeug.security import check_password_hash

# Load the trained Logistic Regression model and vectorizer
model_path = os.path.join('MODELS', 'logistic_regression_model.pkl')
vectorizer_path = os.path.join('MODELS', 'tfidf_vectorizer.pkl')

with open(model_path, 'rb') as model_file:
    model = pickle.load(model_file)

with open(vectorizer_path, 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

def check_login_attempt(user, request):
    # Use the email and password fields from the login form
    email_input = request.form.get('email', '')
    password_input = request.form.get('password', '')
    
    # First check for SQL injection patterns in both inputs
    inputs_to_check = [email_input, password_input]
    max_malicious_prob = 0
    max_suspicious_prob = 0
    
    for input_text in inputs_to_check:
        login_vector = vectorizer.transform([input_text])
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(login_vector)[0]
            malicious_prob = probabilities[1]
        else:
            # fallback: use decision_function or predict
            malicious_prob = float(model.predict(login_vector)[0])
        max_malicious_prob = max(max_malicious_prob, malicious_prob)
        max_suspicious_prob = max(max_suspicious_prob, malicious_prob)
    
    malicious_threshold = 0.7
    suspicious_threshold = 0.3
    
    # If SQL injection is detected, mark as malicious regardless of credentials
    if max_malicious_prob >= malicious_threshold:
        return 'malicious'
    
    # If no SQL injection, then check credentials
    if not user:
        return 'suspicious'
        
    if not check_password_hash(user.password, password_input):
        return 'suspicious'
    
    # If we get here, it's a valid login with no SQL injection
    return 'safe' 
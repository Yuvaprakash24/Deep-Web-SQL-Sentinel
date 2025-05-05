import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
import os

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('MODELS/SQLiV3.csv', encoding='latin1')

# Clean the data
print("Cleaning data...")
df['Sentence'] = df['Sentence'].fillna('')  # Replace NaN with empty string
df['Label'] = pd.to_numeric(df['Label'], errors='coerce').fillna(0).astype(int)  # Convert to int and handle NaN

# Prepare the data
X = df['Sentence']
y = df['Label']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and fit the vectorizer
print("Creating TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train the model
print("Training Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_tfidf, y_train)

# Evaluate the model
print("Evaluating model...")
train_score = model.score(X_train_tfidf, y_train)
test_score = model.score(X_test_tfidf, y_test)
print(f"Training accuracy: {train_score:.4f}")
print(f"Testing accuracy: {test_score:.4f}")

# Train and save Logistic Regression model
print("Training Logistic Regression model...")
logreg_model = LogisticRegression(max_iter=1000, random_state=42)
logreg_model.fit(X_train_tfidf, y_train)

logreg_train_score = logreg_model.score(X_train_tfidf, y_train)
logreg_test_score = logreg_model.score(X_test_tfidf, y_test)
print(f"Logistic Regression Training accuracy: {logreg_train_score:.4f}")
print(f"Logistic Regression Testing accuracy: {logreg_test_score:.4f}")

# Save the model and vectorizer
print("Saving model and vectorizer...")
os.makedirs('MODELS/models', exist_ok=True)

with open('MODELS/random_forest_model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('MODELS/tfidf_vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

with open('MODELS/logistic_regression_model.pkl', 'wb') as logreg_model_file:
    pickle.dump(logreg_model, logreg_model_file)

print("Model training and saving completed successfully!") 
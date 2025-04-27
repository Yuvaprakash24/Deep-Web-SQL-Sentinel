# Import Libraries
import pandas as pd  # type: ignore
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

# Step 1: Load the Dataset
dataset_path = os.path.join('datasets', 'SQLiV3.csv')  # Updated path to the dataset
data = pd.read_csv(dataset_path)  # Ensure SQLiV3.csv is in the datasets folder
print("Dataset Loaded Successfully!")

# Step 2: Inspect the Dataset
print("First 5 rows of the dataset:")
print(data.head())

print("\nDataset Info:")
print(data.info())

# Step 3: Preprocess the Dataset

# Drop rows where 'Sentence' or 'Label' is missing
data = data.dropna(subset=['Sentence', 'Label'])
print("\nDropped rows with missing 'Sentence' or 'Label' values.")

# Clean 'Label' column (remove whitespaces, if any)
data['Label'] = data['Label'].astype(str).str.strip()

# Keep only rows where 'Label' is '1' or '0'
valid_labels = ['0', '1']
data = data[data['Label'].isin(valid_labels)]

print("\nFiltered dataset to include only valid labels ('0' and '1').")

# Convert 'Label' to integer
data['Label'] = data['Label'].astype(int)
print("Target column encoded successfully!")

# Step 4: Convert Text Data to Numerical Format (TF-IDF Vectorization)
print("\nConverting text data to numerical format using TF-IDF...")
vectorizer = TfidfVectorizer(max_features=5000)  # Limit features to 5000 for efficiency
X = vectorizer.fit_transform(data['Sentence'])  # Apply TF-IDF on the 'Sentence' column
y = data['Label']  # Target column

print("\nText data converted to numerical format (TF-IDF).")

# Step 5: Split Dataset into Train and Test Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("\nData split into train and test sets.")

# Step 6: Train Random Forest Classifier
print("\nTraining the Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("Model training completed!")

# Step 7: Evaluate the Model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Step 8: Save the Trained Model and Vectorizer to Files
model_filename = os.path.join('models', 'random_forest_model.pkl')
vectorizer_filename = os.path.join('models', 'tfidf_vectorizer.pkl')

with open(model_filename, 'wb') as model_file:
    pickle.dump(model, model_file)

with open(vectorizer_filename, 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

print(f"\nTrained model saved as '{model_filename}'.")
print(f"TF-IDF vectorizer saved as '{vectorizer_filename}'.")

import pickle
import os

# Load the trained model and vectorizer
model_path = os.path.join('models', 'random_forest_model.pkl')
vectorizer_path = os.path.join('models', 'tfidf_vectorizer.pkl')

with open(model_path, 'rb') as model_file:
    model = pickle.load(model_file)

with open(vectorizer_path, 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

def check_login_attempt(user, request):
    # Extract relevant information from the login attempt
    login_data = f"{user.username} {request.remote_addr} {request.user_agent.string}"
    
    # Vectorize the login data using the loaded TF-IDF vectorizer
    login_vector = vectorizer.transform([login_data])
    
    # Predict the login attempt using the trained model
    prediction = model.predict(login_vector)
    
    # Return 'safe' or 'malicious' based on the prediction
    return 'safe' if prediction[0] == 0 else 'malicious'

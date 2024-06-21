import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
import joblib

# Load the dataset
df = pd.read_csv('messages_dataset.csv')

# Split data into features and labels
X = df['message']
y = df['target']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create pipelines for each classifier
pipeline_dt = Pipeline([
    ('vectorizer', TfidfVectorizer()),  
    ('classifier', DecisionTreeClassifier())
])

pipeline_rf = Pipeline([
    ('vectorizer', TfidfVectorizer()),  
    ('classifier', RandomForestClassifier())
])

pipeline_nb = Pipeline([
    ('vectorizer', TfidfVectorizer()),  
    ('classifier', MultinomialNB())
])

# Train each model
pipelines = {
    'Decision Tree': pipeline_dt,
    'Random Forest': pipeline_rf,
    'Naive Bayes': pipeline_nb
}

for name, pipeline in pipelines.items():
    print(f"Training {name}...")
    pipeline.fit(X_train, y_train)
    accuracy = pipeline.score(X_test, y_test)
    print(f"{name} Accuracy:", accuracy)
    print()

# Choose the best model based on accuracy
best_model_name = max(pipelines, key=lambda x: pipelines[x].score(X_test, y_test))
best_model = pipelines[best_model_name]
print(f"Best Model: {best_model_name}")

# Save the best model to a file
joblib.dump(best_model, f'best_message_classifier.pkl')

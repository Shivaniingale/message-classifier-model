import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, precision_score, f1_score, ConfusionMatrixDisplay
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv('dataset.csv')

# Split data into features and labels
X = df['message']
y = df['target']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=50)

# Create a pipeline that includes TF-IDF vectorization and the random forest classifier
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('classifier', RandomForestClassifier())
])

# Define hyperparameters for grid search
parameters = {
    'vectorizer__ngram_range': [(1, 1), (1, 2)],  # Uni-gram and bi-gram
    'vectorizer__max_df': (0.5, 0.75, 1.0),
    'vectorizer__min_df': (1, 2),
    'classifier__n_estimators': [100, 200, 300],
    'classifier__max_depth': [None, 10, 20, 30],
}

# Perform grid search to find the best hyperparameters
grid_search = GridSearchCV(pipeline, parameters, cv=5, n_jobs=-1)
grid_search.fit(X_train, y_train)

# Print the best hyperparameters
print("Best hyperparameters:", grid_search.best_params_)

# Calculate and print the accuracy
accuracy = grid_search.best_estimator_.score(X_test, y_test)
print("Model Accuracy:", accuracy)

# Predict on the test set
y_pred = grid_search.predict(X_test)

# Calculate and print the confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:\n", conf_matrix)

# Plot the confusion matrix
plt.figure(figsize=(10, 7))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Safe', 'Unsafe'], yticklabels=['Safe', 'Unsafe'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

# Calculate and print the precision score
precision = precision_score(y_test, y_pred)
print("Precision Score:", precision)

# Calculate and print the F1 score
f1 = f1_score(y_test, y_pred)
print("F1 Score:", f1)

# Save the best model to a file
joblib.dump(grid_search.best_estimator_, 'message_classifier.pkl')

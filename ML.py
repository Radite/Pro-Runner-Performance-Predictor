import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score
import numpy as np

# Load the dataset
data = pd.read_csv('TrainingData.csv')

# Convert 'Event Date' to a datetime object and extract relevant features (like month)
data['Event Date'] = pd.to_datetime(data['Event Date'], errors='coerce')
data['Event Month'] = data['Event Date'].dt.month

# Select features and target
features = ['Gender', 'Country', 'Distance', 'Event Month', 'Wind', 'Altitude', 'Age']
target = 'RaceTime'

# Preprocessing for numerical and categorical data
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['Distance', 'Wind', 'Altitude', 'Age', 'Event Month']),
        ('cat', OneHotEncoder(), ['Gender', 'Country'])
    ])

# Split the data into training and testing sets
X = data[features]
y = data[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# List of models to train
models = [
    ('Linear Regression', LinearRegression()),
    ('Ridge Regression', Ridge()),
    ('Random Forest', RandomForestRegressor()),
    ('Gradient Boosting', GradientBoostingRegressor()),
    ('Support Vector Regression', SVR()),
    ('K-Nearest Neighbors', KNeighborsRegressor())
]

# Dictionary to store the scores
model_scores = {}

# Train and evaluate each model
for name, model in models:
    # Create a pipeline that transforms the data and then fits the model
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
    
    # Train the model using cross-validation
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='r2')
    
    # Mean R-squared score
    mean_cv_score = np.mean(cv_scores)
    model_scores[name] = mean_cv_score
    print(f'{name} cross-validated mean R-squared: {mean_cv_score:.4f}')
    
    # Train the pipeline on the full training data
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    # Test R-squared score
    test_r2_score = r2_score(y_test, y_pred)
    print(f'{name} test R-squared: {test_r2_score:.4f}')

# Find the best model based on the mean cross-validated R-squared
best_model_name = max(model_scores, key=model_scores.get)
print(f'Best model based on cross-validation: {best_model_name}')

# If you want to use the best model for predictions later
# best_pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', models[best_model_name])])
# best_pipeline.fit(X_train, y_train)
# y_pred_new = best_pipeline.predict(X_new)

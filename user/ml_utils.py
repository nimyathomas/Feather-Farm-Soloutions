import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from .models import BatchPerformanceData, BatchPrediction

class BatchPerformancePredictor:
    def __init__(self):
        self.weight_model = RandomForestRegressor()
        self.fcr_model = RandomForestRegressor()
        self.feed_model = RandomForestRegressor()
        self.scaler = StandardScaler()
        
    def prepare_data(self):
        # Get all performance data
        data = BatchPerformanceData.objects.all().values()
        df = pd.DataFrame(data)
        
        # Features for prediction
        features = ['age_in_days', 'temperature', 'humidity', 
                   'feed_consumption', 'water_consumption', 'mortality_rate']
        
        # Target variables
        targets = ['average_weight', 'fcr', 'feed_consumption']
        
        X = df[features]
        y_weight = df['average_weight']
        y_fcr = df['fcr']
        y_feed = df['feed_consumption']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y_weight, y_fcr, y_feed
    
    def train_models(self):
        X, y_weight, y_fcr, y_feed = self.prepare_data()
        
        # Split data
        X_train, X_test, y_weight_train, y_weight_test = train_test_split(
            X, y_weight, test_size=0.2, random_state=42
        )
        
        # Train models
        self.weight_model.fit(X_train, y_weight_train)
        self.fcr_model.fit(X_train, y_fcr[y_weight_train.index])
        self.feed_model.fit(X_train, y_feed[y_weight_train.index])
        
        return {
            'weight_score': self.weight_model.score(X_test, y_weight_test),
            'fcr_score': self.fcr_model.score(X_test, y_fcr[y_weight_test.index]),
            'feed_score': self.feed_model.score(X_test, y_feed[y_weight_test.index])
        }
    
    def predict_batch_performance(self, batch_data):
        # Scale input data
        scaled_data = self.scaler.transform(batch_data)
        
        # Make predictions
        weight_pred = self.weight_model.predict(scaled_data)
        fcr_pred = self.fcr_model.predict(scaled_data)
        feed_pred = self.feed_model.predict(scaled_data)
        
        # Calculate confidence scores
        weight_conf = self.weight_model.predict_proba(scaled_data).max(axis=1)
        
        return {
            'predicted_weight': weight_pred[0],
            'predicted_fcr': fcr_pred[0],
            'predicted_feed': feed_pred[0],
            'confidence': weight_conf[0]
        } 
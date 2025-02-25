import pandas as pd
import pickle
import os
from datetime import datetime
from django.conf import settings

class ChickGrowthPredictor:
    def __init__(self):
        self.model = self.load_model()

    def load_model(self):
        """Load the trained XGBoost model"""
        model_path = os.path.join(settings.BASE_DIR, 'stakeholder', 'models', 'xgb_regressor.pkl')
        try:
            with open(model_path, 'rb') as file:
                model = pickle.load(file)
                print("Model loaded successfully")  # Debug print
                return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def prepare_features(self, data):
        """Prepare features for prediction"""
        try:
            print("Preparing features with data:", data)  # Debug print
            
            # Convert input data to correct types
            features = pd.DataFrame({
                'Day': [int(data['day_number'])],
                'Feed_Taken_kg': [float(data['feed_taken'])],
                'Water_Taken_L': [float(data['water_taken'])],
                'Temperature_C': [float(data['temperature'])],
                'Alive_Count': [int(data['alive_count'])]  # Keep temporarily for calculations
            })
            
            print("Base features created:", features)  # Debug print
            
            # Calculate per chick metrics
            features['Feed_per_Chick'] = features['Feed_Taken_kg'] / features['Alive_Count']
            features['Water_per_Chick'] = features['Water_Taken_L'] / features['Alive_Count']
            
            # Remove Alive_Count as it wasn't in training data
            features = features.drop('Alive_Count', axis=1)
            
            print("Final features:", features)  # Debug print
            return features
            
        except Exception as e:
            print(f"Error preparing features: {e}")  # Debug print
            raise Exception(f"Feature preparation failed: {str(e)}")

    def get_expected_weight_range(self, day):
        """Get expected weight range for a given day"""
        # Standard weight ranges for broiler chickens (in grams)
        # Updated ranges with wider tolerances
        weight_ranges = {
            1: {'min': 40, 'target': 55, 'max': 70},
            2: {'min': 80, 'target': 95, 'max': 115},
            3: {'min': 120, 'target': 140, 'max': 165},
            4: {'min': 165, 'target': 185, 'max': 215},
            5: {'min': 215, 'target': 240, 'max': 275},
            6: {'min': 270, 'target': 300, 'max': 340},
            7: {'min': 330, 'target': 370, 'max': 420},
            14: {'min': 850, 'target': 950, 'max': 1150},
            21: {'min': 1700, 'target': 1900, 'max': 2300},
            28: {'min': 2500, 'target': 2800, 'max': 3400},
            35: {'min': 3300, 'target': 3700, 'max': 4500},
            40: {'min': 4200, 'target': 4700, 'max': 5700}
        }
        
        # Find the closest day in our ranges
        available_days = sorted(weight_ranges.keys())
        closest_day = min(available_days, key=lambda x: abs(x - day))
        return weight_ranges[closest_day]

    def predict(self, data):
        """Make prediction and determine growth status"""
        try:
            print("Starting prediction with data:", data)  # Debug print
            
            if not self.model:
                raise Exception("Model not loaded")

            # Prepare features
            features = self.prepare_features(data)
            day_number = int(data['day_number'])
            
            # Make prediction
            predicted_weight = float(self.model.predict(features)[0])
            print(f"Raw prediction: {predicted_weight}")  # Debug print
            
            # Get expected weight range for this day
            weight_range = self.get_expected_weight_range(day_number)
            print(f"Expected weight range for day {day_number}:", weight_range)  # Debug print
            
            # Calculate percentage difference from target
            target_weight = weight_range['target']
            percent_diff = ((predicted_weight - target_weight) / target_weight) * 100
            print(f"Percentage difference from target: {percent_diff:.2f}%")  # Debug print
            
            # Determine growth status with percentage-based thresholds
            if predicted_weight < weight_range['min']:
                deviation = ((weight_range['min'] - predicted_weight) / weight_range['min']) * 100
                status = "Under-Growing"
                print(f"Under-growing by {deviation:.2f}%")
            elif predicted_weight > weight_range['max']:
                deviation = ((predicted_weight - weight_range['max']) / weight_range['max']) * 100
                status = "Over-Growing"
                print(f"Over-growing by {deviation:.2f}%")
            else:
                status = "On Track"
                print("Weight is within expected range")
            
            # Calculate weight difference if actual weight is provided
            actual_weight = data.get('actual_weight')
            if actual_weight and actual_weight != '':
                actual_weight = float(actual_weight)
                weight_diff = actual_weight - predicted_weight
            else:
                weight_diff = None

            result = {
                'success': True,
                'predicted_weight': round(predicted_weight, 2),
                'weight_difference': round(weight_diff, 2) if weight_diff is not None else None,
                'growth_status': status,
                'expected_range': {
                    'min': weight_range['min'],
                    'target': weight_range['target'],
                    'max': weight_range['max']
                },
                'percent_difference': round(percent_diff, 2)
            }
            print("Prediction result:", result)  # Debug print
            return result
            
        except Exception as e:
            print(f"Error in prediction: {e}")  # Debug print
            raise Exception(f"Prediction failed: {str(e)}")
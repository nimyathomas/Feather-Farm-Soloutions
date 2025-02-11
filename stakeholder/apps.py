from django.apps import AppConfig
import tensorflow as tf
import os

class StakeholderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stakeholder'

    def ready(self):
        """Load the model globally when Django starts."""
        global disease_model
        model_path = os.path.join(self.path, 'models', 'poultry_disease_classifier.h5')
        
        if os.path.exists(model_path):
            disease_model = tf.keras.models.load_model(model_path)
            print(f"✅ Model loaded from {model_path}")
        else:
            disease_model = None
            print("❌ Model file not found.")

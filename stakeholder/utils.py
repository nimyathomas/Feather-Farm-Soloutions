# # stakeholder/utils.py

import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Load your trained models
CNN_MODEL_PATH = os.path.join(settings.BASE_DIR, 'stakeholder', 'models', 'best_cnn.h5')
MOBILENET_MODEL_PATH = os.path.join(settings.BASE_DIR, 'stakeholder', 'models', 'mobilenet_model.h5')

# Try to load CNN model
try:
    cnn_model = tf.keras.models.load_model(CNN_MODEL_PATH)
    print(f"CNN model loaded successfully from {CNN_MODEL_PATH}")
except Exception as e:
    print(f"Error loading CNN model: {str(e)}")
    cnn_model = None

# Try to load MobileNetV2 model
try:
    mobilenet_model = tf.keras.models.load_model(MOBILENET_MODEL_PATH)
    print(f"MobileNetV2 model loaded successfully from {MOBILENET_MODEL_PATH}")
except Exception as e:
    print(f"Error loading MobileNetV2 model: {str(e)}")
    mobilenet_model = None

# Define class mappings based on your notebook
CLASS_NAMES = ['Coccidiosis', 'Healthy', 'New Castle Disease', 'Salmonella']

def predict_disease(image_file):
    """
    Multi-stage disease prediction using ensemble of CNN and MobileNetV2 models
    """
    try:
        # Preprocess image
        img = Image.open(image_file).convert('RGB')
        img = img.resize((128, 128))  # Match the size used in your notebook
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Check if models are loaded
        if cnn_model is None or mobilenet_model is None:
            return {
                "error": "Models not loaded properly",
                "disease": "Error",
                "confidence": 0.0,
                "all_probabilities": {name: 0.0 for name in CLASS_NAMES}
            }
        
        # Get predictions from both models
        cnn_preds = cnn_model.predict(img_array)[0]
        mobilenet_preds = mobilenet_model.predict(img_array)[0]
        
        # Ensemble predictions (average)
        ensemble_preds = (cnn_preds + mobilenet_preds) / 2
        
        # Get predicted class and confidence
        predicted_class_index = np.argmax(ensemble_preds)
        predicted_class = CLASS_NAMES[predicted_class_index]
        confidence = float(ensemble_preds[predicted_class_index]) * 100
        
        # Create result dictionary
        result = {
            "disease": predicted_class,
            "confidence": confidence,
            "all_probabilities": {CLASS_NAMES[i]: float(ensemble_preds[i]) * 100 for i in range(len(CLASS_NAMES))}
        }
        
        # Implement multi-stage logic
        # Stage 1: Binary classification (Healthy vs Diseased)
        healthy_index = CLASS_NAMES.index('Healthy')
        healthy_prob = ensemble_preds[healthy_index]
        is_diseased = predicted_class_index != healthy_index
        
        # If diseased, add severity based on confidence
        if is_diseased:
            # Calculate severity based on confidence and distance from healthy probability
            disease_confidence = confidence
            healthy_confidence = float(ensemble_preds[healthy_index]) * 100
            confidence_gap = disease_confidence - healthy_confidence
            
            if confidence_gap > 50 or disease_confidence > 85:
                severity = "High"
            elif confidence_gap > 30 or disease_confidence > 70:
                severity = "Medium"
            else:
                severity = "Low"
                
            result["severity"] = severity
        else:
            result["severity"] = "None"
        
        return result
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "disease": "Error",
            "confidence": 0.0,
            "all_probabilities": {name: 0.0 for name in CLASS_NAMES}
        }

print("UTILS MODULE LOADED SUCCESSFULLY")

@login_required
def test_utils(request):
    from .utils import predict_disease
    return JsonResponse({"message": "Utils module imported successfully"})

# # stakeholder/utils.py

# import tensorflow as tf
# import numpy as np
# from PIL import Image
# import io

# # --- Define your desired class mapping and reverse mapping ---
# # Desired mapping: keys are class names, values are indices
# desired_mapping = {
#     'Coccidiosis': 0,
#     'Healthy': 1,
#     'New Castle Disease': 2,
#     'Salmonella': 3
# }

# # Create a reverse mapping (index to class name)
# reverse_mapping = {v: k for k, v in desired_mapping.items()}

# # --- Preprocessing function (if not already defined) ---
# def preprocess_image(image):
#     """Preprocess image for model prediction."""
#     try:
#         if image.mode != 'RGB':
#             image = image.convert('RGB')
#         image = image.resize((150, 150))  # Ensure this matches training
#         image_array = np.array(image) / 255.0
#         image_array = np.expand_dims(image_array, axis=0)
#         return image_array
#     except Exception as e:
#         print(f"Error in preprocess_image: {str(e)}")
#         raise

# # --- Prediction function ---
# def predict_disease(image_file):
#     """ML-based disease detection"""
#     print("🔵 UTILS.PY VERSION OF predict_disease CALLED 🔵")
#     try:
#         # Check if model is loaded
#         if disease_model is None:
#             return {"disease": "Error", "confidence": "0.00%"}
        
#         # Open and process the image
#         if isinstance(image_file, Image.Image):
#             img = image_file
#         else:
#             image_data = image_file.read()
#             img = Image.open(io.BytesIO(image_data))
        
#         processed_image = preprocess_image(img)
#         predictions = disease_model.predict(processed_image, verbose=0)
#         predictions = predictions[0]  # Get the first (and only) prediction array
        
#         # Use our desired mapping via reverse_mapping
#         predicted_index = np.argmax(predictions)
#         predicted_class = reverse_mapping[predicted_index]
#         confidence_score = float(predictions[predicted_index]) * 100
        
#         print(f"Debug - Raw Predictions: {predictions}")
#         print(f"Debug - Predicted Index: {predicted_index}")
#         print(f"Debug - Predicted Disease: {predicted_class}")
#         print(f"Debug - Confidence: {confidence_score:.2f}%")
        
#         return {"disease": predicted_class, "confidence": f"{confidence_score:.2f}%"}
        
#     except Exception as e:
#         print(f"Error in predict_disease: {str(e)}")
#         return {"disease": "Error", "confidence": "0.00%"}

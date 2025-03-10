from django.db import IntegrityError
from .models import FeedMonitoring, ChickBatch, DiseaseAnalysis, FeedCalculator
from django.shortcuts import render, redirect
from .forms import BatchSelectionForm, ChickenBatchForm, CompletedBatchUpdateForm
from django.shortcuts import render
from .forms import DailyComparisonForm
from .forms import DailyComparisonForm  # Ensure this is the correct import
from sklearn.preprocessing import MinMaxScaler

from django.shortcuts import get_object_or_404, redirect
from .forms import DailyDataForm
from .models import ChickBatch, DailyData  # Adjust based on your models
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg
from .forms import DailyDataForm  # Assume you have created a form for DailyData
from .models import ChickBatch, DailyData, Post, Comment
from pyowm import OWM
from datetime import timedelta
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.http import HttpResponse, FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from stakeholder.models import ChickBatch
from user.models import User, FeedStock
from django.urls import reverse
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .forms import StakeholderUserForm, FarmForm  # Import your forms
from .models import Farm  # Import your models

import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import io
import os
from django.conf import settings
import tensorflow as tf

from .forms import FeedStockForm  # Add this import

from datetime import datetime
from django.db.models import Sum, F
from xhtml2pdf import pisa
import csv
from .forms import DailyFeedConsumptionForm
from .models import ChickBatch, FeedAssignment, DailyFeedConsumption
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import reverse

from user.models import Vaccine  # Import from user app instead of stakeholder
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from django.http import JsonResponse
from django.db.models import F
from .models import ChickBatch, VaccinationSchedule  # Add this import
from user.models import Vaccine  # Add this import
from .models import ChickBatch, VaccinationSchedule, VaccinationAuditLog  # Add VaccinationAuditLog

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import ChickBatch, GrowthPrediction
from .prediction_system import ChickGrowthPredictor
# Add this import at the top of your file (around line 66-67)
from django.db import models

# Then your existing imports continue...
from datetime import datetime
from django.http import JsonResponse
from django.db.models import F

# Add this import at the top of your file (around line 94-95)
# from .utils import predict_disease  # Import from local utils.py file
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
import razorpay
import json
from decimal import Decimal
from .models import ChickBatch, Farm, StakeholderPayment# Add user_passes_test here
import razorpay
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
import io
import base64
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import label_binarize



# At the top of views.py, add this debug code
# MODEL_PATH = os.path.join(settings.BASE_DIR, 'stakeholder', 'models', 'poultry_disease_classifier_retrained.h5')
# print(f"\nAttempting to load model from: {MODEL_PATH}")
# print(f"File exists: {os.path.exists(MODEL_PATH)}")

# try:
#     if os.path.exists(MODEL_PATH):
#         model = tf.keras.models.load_model(MODEL_PATH)
#         # Test model with random data
#         test_input = np.random.random((1, 150, 150, 3))
#         test_pred = model.predict(test_input)
#         print("\nModel test prediction shape:", test_pred.shape)
#         print("Model loaded and tested successfully")
#     else:
#         print("Model file not found!")
#         model = None
# except Exception as e:
#     print(f"Error loading model: {str(e)}")
#     model = None

# CLASS_MAPPING = {
#     0: "Coccidiosis",
#     1: "Healthy",
#     2: "New Castle Disease",
#     3: "Salmonella"
# }

# def predict_disease(image_file):
#     """ML-based disease detection"""
#     print("🔴 VIEWS.PY VERSION OF predict_disease CALLED 🔴")


#     try:
#         # Preprocess image
#         img = Image.open(image_file).convert('RGB')
#         img = img.resize((150, 150))
#         img_array = np.array(img) / 255.0
#         img_array = np.expand_dims(img_array, axis=0)

#         # Make prediction using model
#         if model is not None:
#             # Get model predictions with debug info
#             prediction = model.predict(img_array)
#             print("\nRaw Predictions:", prediction[0])  # Debug print
            
#             predicted_class = np.argmax(prediction[0])
#             confidence = float(prediction[0][predicted_class]) * 100
            
#             # Print debug information
#             print(f"\nPredicted Class Index: {predicted_class}")
#             print(f"Class Mapping: {CLASS_MAPPING}")
#             print(f"Predicted Disease: {CLASS_MAPPING[predicted_class]}")
#             print(f"Confidence: {confidence:.2f}%")
            
#             # Add probabilities for all classes
#             all_probs = {
#                 CLASS_MAPPING[i]: f"{float(prediction[0][i])*100:.2f}%"
#                 for i in range(len(CLASS_MAPPING))
#             }
#             print("\nAll Probabilities:", all_probs)
            
#             return {
#                 "disease": CLASS_MAPPING[predicted_class],
#                 "confidence": f"{confidence:.2f}%",
#                 "severity": "High" if confidence > 80 else "Medium" if confidence > 60 else "Low",
#                 "symptoms": get_disease_symptoms(CLASS_MAPPING[predicted_class].lower()),
#                 "all_probabilities": all_probs
#             }
#         else:
#             print("Model is None - falling back to rule-based prediction")
#             return {
#                 "disease": "Error",
#                 "confidence": "0.00%",
#                 "severity": "Unknown",
#                 "symptoms": [],
#                 "error": "Model not loaded properly"
#             }
#     except Exception as e:
#         print(f"Error in prediction: {str(e)}")
#         return {"error": f"Analysis failed: {str(e)}"}

def add_or_edit_farm(request, id):
    # Fetch the user by ID
    user = get_object_or_404(User, id=id)

    # If the user already has a farm, fetch it; otherwise, create a new instance
    farm = Farm.objects.filter(owner=user).first() or Farm(owner=user)

    # Initialize the forms with default values
    user_form = StakeholderUserForm(instance=user)
    farm_form = FarmForm(instance=farm)

    if request.method == "POST":
        if "update_profile" in request.POST:
            # Handle Profile Update
            user_form = StakeholderUserForm(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("stakeholder")
            else:
                messages.error(
                    request, "Error updating the profile. Check the form and try again."
                )

        elif "update_farm" in request.POST:  # Handle Farm Details Update
            farm_form = FarmForm(request.POST, request.FILES, instance=farm)
            print("POST data:", request.POST)
            print("FILES datas:", farm_form.errors)
            if farm_form.is_valid():
                latitude = farm_form.cleaned_data.get("latitude")
                longitude = farm_form.cleaned_data.get("longitude")

                # Ensure latitude and longitude are valid numbers
                if latitude is None or longitude is None:

                    messages.error(request, "Latitude and Longitude must be provided.")
                else:
                    print("in form instance")
                    farm_instance = farm_form.save(commit=False)
                    print("in if")
                    farm_instance.owner = user
                    farm_instance.save()
                    messages.success(request, "Farm details updated successfully.")
                    return redirect("stakeholder")
            else:
                print(f"Form errors: {farm_form.errors}")
                messages.error(
                    request,
                    "Error updating farm details. Check the form and try again.",
                )

    # Render the template with both forms
    return render(
        request,
        "stakeholder_profile.html",
        {
            "user_form": user_form,
            "farm_form": farm_form,
            "farm": farm,  # Pass the farm object to access fields in the template
        },
    )


@login_required
def stakeholder(request):
    user = request.user  # Assuming the user is logged in
    today = timezone.now().date()

    farm = Farm.objects.filter(owner=user).first()
    try:
        # Ensure farm has chick_batches attribute
            if hasattr(farm, 'chick_batches'):
                 chick_batches = farm.chick_batches.all().order_by("-batch_date")
                 total_chick_count = sum(batch.initial_chick_count for batch in chick_batches)
            else:
                chick_batches = []
                total_chick_count = 0  # Default value if attribute is missing
    except AttributeError as e:
        chick_batches = []
        total_chick_count = 0
        print(f"Error: {e}")  # Log the error for debugging

# Fetch location from query parameters
    latitude = request.GET.get("lat")
    longitude = request.GET.get("lon")


    # Set up OpenWeatherMap client
    api_key = "6a0179abe35c7736af4f3f57bd4da77e"
    owm = OWM(api_key)

    # Create a WeatherManager instance
    # This should be correct if you're using the right version
    mgr = owm.weather_manager()

    # Fetch weather data based on coordinates or use fallback
    if latitude and longitude:
        try:
            observation = mgr.weather_at_coords(float(latitude), float(longitude))
        except Exception as e:
            observation = mgr.weather_at_place("Erattupetta")  # Fallback
    else:
        observation = mgr.weather_at_place("Erattupetta")  # Fallback

    weather = observation.weather

    weather_data = {
        "temperature": weather.temperature("celsius")["temp"],
        "humidity": weather.humidity,
        "wind_speed": weather.wind()["speed"],
    }

    # Handle alerts (add your logic here)
    alert_vaccine_dates = []  # Example alert lists
    upliftment_alert_dates = []
    feed_dates = []

    for batch in chick_batches:
        batch_date = batch.batch_date

        # Calculate vaccination and upliftment dates
        alert_vaccine_dates.append(
            {
                "7th_day": batch_date + timedelta(days=6),
                "14th_day": batch_date + timedelta(days=13),
                "21st_day": batch_date + timedelta(days=20),
                "batch": batch,
            }
        )

        upliftment_alert_dates.append(batch_date + timedelta(days=39))

        # Feed stage reminders (pre-starter, starter, finisher)
        feed_dates.append(
            {
                "pre_starter": batch_date,
                "starter": batch_date + timedelta(days=9),
                "finisher": batch_date + timedelta(days=23),
                "batch": batch,
            }
        )

    # Populate alerts as per your logic...

    context = {
        "chick_batches": chick_batches,
        "total_chick_count": total_chick_count,
        "today": today,
        "user_data": user,
        "farm_data": farm,
        "weather_data": weather_data,
        "alert_vaccine_dates": alert_vaccine_dates,
        "upliftment_alert_dates": upliftment_alert_dates,
        "feed_dates": feed_dates,
    }

    return render(request, "stakeholderdash.html", context)


def home(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def services(request):
    return render(request, "services.html")


def contact(request):
    return render(request, "contact.html")


def logout_view(request):
    logout(request)
    return redirect('login')  # or whatever URL you want to redirect to after logout


# views.py


def calculate_feeders_and_drinkers(initial_chick_count):
    feeders = initial_chick_count // 50  # 1 feeder for every 50 chicks
    drinkers = initial_chick_count // 50  # 1 drinker for every 50 chicks
    return feeders, drinkers


def stateholder_batch(request):
    user = request.user  # Assuming the user is logged in
    farm = Farm.objects.filter(owner=user.id).first()
    chick_batches = farm.chick_batches.all().order_by("-batch_date")

    # Prepare to store batch-wise feeders and drinkers
    batch_info = []
    total_profit = 0
    for batch in chick_batches:
        initial_chick_count = batch.initial_chick_count
        feeders, drinkers = calculate_feeders_and_drinkers(initial_chick_count)
        batch_info.append(
            {
                "batch": batch,
                "initial_chick_count": initial_chick_count,
                "feeders_required": feeders,
                "drinkers_required": drinkers,
            }
        )
    completed_batches = ChickBatch.objects.filter(batch_status="completed", user=user)
    for batch in completed_batches:
        total_weight = batch.total_weight  # Using the @property method
        price_per_kg = batch.price_per_kg
        if total_weight > 0 and price_per_kg:
            # Add the profit for this batch
            total_profit += total_weight * float(price_per_kg)
    total_chick_count = sum(batch.initial_chick_count for batch in chick_batches)
    context = {
        "batch_info": batch_info,  # Updated to pass batch information
        "total_chick_count": total_chick_count,
        "user_data": user,
        "total_profit": total_profit,
    }
    return render(request, "stakeholderbatch.html", context)


def update_chick_count(request, id):
    if request.method == "POST":
        try:
            # Get the current logged-in user
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect(reverse("stakeholderuserprofile", args=[id]))

        # Get chick count and other details from the form
        initial_chick_count = request.POST.get("initial_chick_count")
        batch_type = request.POST.get("batch_type")
        batch_size = request.POST.get("batch_size")
        price_per_kg = request.POST.get("price_per_kg")
        price_per_batch = request.POST.get("price_per_batch")

        # Validate initial chick count
        try:
            initial_chick_count = int(initial_chick_count)
            if initial_chick_count < 0:
                raise ValueError("Chick count cannot be negative.")
        except ValueError:
            messages.error(request, "Invalid chick count value.")
            return redirect(reverse("stakeholderuserprofile", args=[id]))

        # Calculate coop capacity based on user's length and breadth
        coop_capacity = 0
        if user.length and user.breadth:
            sqr_feet = user.length * user.breadth
            coop_capacity = sqr_feet * 4  # 4 birds per sq ft
        else:
            messages.error(
                request,
                "Please ensure that the coop's length and breadth are provided.",
            )
            return redirect(reverse("stakeholderuserprofile", args=[id]))

        # Validate that the entered chick count does not exceed the coop capacity
        if initial_chick_count > coop_capacity:
            messages.error(
                request,
                f"You can't add more than {coop_capacity} birds for the current coop size.",
            )
            return redirect(reverse("stakeholderuserprofile", args=[id]))

        # Create a new ChickBatch record for the current user
        chick_batch = ChickBatch.objects.create(
            user=user,
            initial_chick_count=initial_chick_count,
            batch_date=timezone.now(),
            batch_type=batch_type,
            batch_size=batch_size,
            # price_per_kg=price_per_kg,
            # price_per_batch=price_per_batch
        )

        # After creation, call method to calculate and set batch price
        chick_batch.batch_chicken_price()  # Ensure price is calculated
        chick_batch.available_chickens += initial_chick_count
        chick_batch.save()

        messages.success(request, "Chick batch successfully added.")
        return redirect("stakeholderuser")

    # If not POST, redirect back to the user profile
    return redirect(reverse("stakeholderuserprofile", args=[id]))


def feed_request(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "feed_request.html")


def vaccination(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "vaccinations.html", {"user": user})


@login_required
def add_daily_data(request):
    try:
        if request.method == 'POST':
            # Get the batch
            batch_id = request.POST.get('batch')
            if not batch_id:
                messages.error(request, "Please select a batch")
                return redirect('add_daily_data')
            
            batch = get_object_or_404(ChickBatch, id=batch_id)
            
            # Get arrays of data from the form
            dates = request.POST.getlist('date[]')
            alive_counts = request.POST.getlist('alive_count[]')
            sick_chicks = request.POST.getlist('sick_chicks[]')
            mortality_counts = request.POST.getlist('mortality_count[]')
            feed_uplifted = request.POST.getlist('feed_uplifted[]')
            water_consumption = request.POST.getlist('water_consumption[]')
            weight_gain = request.POST.getlist('weight_gain[]')
            temperature = request.POST.getlist('temperature[]')
            
            # Create daily data entry
            daily_data = DailyData.objects.create(
                batch=batch,
                date=dates[0],
                alive_count=alive_counts[0],
                sick_chicks=sick_chicks[0],
                mortality_count=mortality_counts[0],
                feed_uplifted=feed_uplifted[0],
                water_consumption=water_consumption[0],
                weight_gain=weight_gain[0],
                temperature=temperature[0],
                owner=request.user
            )
            
            # Update batch statistics
            batch.live_chick_count = alive_counts[0]
            batch.total_mortality_count = batch.total_mortality_count + int(mortality_counts[0])
            batch.save()
            
            messages.success(request, 'Daily data added successfully!')
            return redirect('list_daily_data', batch_id=batch.id)
        
        # GET request handling
        all_batches = ChickBatch.objects.filter(batch_status='Active').order_by('-batch_date')
        context = {
            'all_batches': all_batches,
        }
        return render(request, 'daily_batch.html', context)
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('add_daily_data')


def calculate_weeks(batch_date):
    weeks = []
    for i in range(6):  # Create 6 weeks
        start_date = batch_date + timedelta(days=i * 7)
        end_date = start_date + timedelta(days=6)
        if i == 5:  # For the 6th week, adjust the end date to only go to day 40
            end_date = batch_date + timedelta(days=39)  # 5 extra days
        weeks.append((start_date, end_date))
    return weeks


def list_daily_data(request, batch_id):
    batch = get_object_or_404(ChickBatch, id=batch_id)
    # Initialize the error message
    error_message = None

    # Get the selected filters from the GET request
    selected_category = request.GET.get("category")
    min_value = request.GET.get("min_value")
    max_value = request.GET.get("max_value")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Validate start_date and end_date
    try:
        if start_date and end_date:
            start_date_obj = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date_obj < batch.batch_date:
                raise ValueError(
                    f"Start date cannot be before the batch start date ({batch.batch_date})."
                )
            if end_date_obj < batch.batch_date:
                raise ValueError(
                    f"End date cannot be before the batch start date ({batch.batch_date})."
                )
    except ValueError as e:
        error_message = str(e)
        start_date = end_date = None  # Reset invalid dates

    # Check for negative min_value and max_value
    if (min_value and int(min_value) < 0) or (max_value and int(max_value) < 0):
        error_message = "Minimum and maximum values cannot be negative."
        min_value = max_value = None  # Reset invalid values

    # Fetch daily data for the batch
    daily_data_records = DailyData.objects.filter(batch=batch).order_by("date")

    # Apply date filtering
    if start_date and end_date:
        daily_data_records = daily_data_records.filter(
            date__range=[start_date, end_date]
        )

    # Apply category filtering with range
    if selected_category in ["weight_gain", "sick_chicks", "mortality_count"]:
        filter_params = {}
        if min_value:
            filter_params[f"{selected_category}__gte"] = min_value
        if max_value:
            filter_params[f"{selected_category}__lte"] = max_value
        daily_data_records = daily_data_records.filter(**filter_params)

    # Check if any records are found
    if not daily_data_records.exists():
        error_message = error_message or "No records found for the given filters."

    # Calculate totals and averages using aggregate
    total_metrics = daily_data_records.aggregate(
        total_sick_chicks=Sum("sick_chicks"),
        total_weight_gain=Sum("weight_gain"),
        total_feed_uplifted=Sum("feed_uplifted"),
        total_water_consumption=Sum("water_consumption"),
        total_mortality_count=Sum("mortality_count"),
        average_temperature=Avg("temperature"),
    )

    # Implement pagination
    paginator = Paginator(daily_data_records, 40)  # Show 10 records per page
    page_obj = paginator.get_page(request.GET.get("page"))
    # Choose the form based on the batch status
    if batch.batch_status == "completed":
        form_class = CompletedBatchUpdateForm
    else:
        form_class = ChickenBatchForm

    if request.method == "POST":
        form = form_class(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            # Redirect to a page that displays the batch details
            return redirect("list_daily_data", batch_id=batch.id)
    else:
        form = form_class(instance=batch)
    # Prepare context
    context = {
        "batch": batch,
        "form": form,
        "daily_data_records": page_obj,
        "selected_category": selected_category,
        "min_value": min_value,
        "max_value": max_value,
        "start_date": start_date,
        "end_date": end_date,
        "total_sick_chicks": total_metrics.get("total_sick_chicks", 0),
        "total_weight_gain": total_metrics.get("total_weight_gain", 0),
        "total_feed_uplifted": total_metrics.get("total_feed_uplifted", 0),
        "total_water_consumption": total_metrics.get("total_water_consumption", 0),
        "average_temperature": total_metrics.get("average_temperature", 0),
        "total_mortality_count": total_metrics.get("total_mortality_count", 0),
        "error_message": error_message,
    }

    return render(request, "list_daily_data.html", context)


def edit_daily_data(request, id):
    # Fetch the specific record or return 404 if not found
    daily_data = get_object_or_404(DailyData, id=id)

    if request.method == "POST":
        # Bind data to the form to process user input
        form = DailyDataForm(request.POST, instance=daily_data)
        if form.is_valid():
            form.save()  # Save changes
            # Redirect back to the list page
            return redirect("list_daily_data", batch_id=daily_data.batch.id)
    else:
        # Display the form with pre-filled data
        form = DailyDataForm(instance=daily_data)

    # Pass the form to the template
    return render(request, "edit_daily_data.html", {"form": form})


def delete_daily_data(request, daily_data_id):
    daily_data_entry = get_object_or_404(DailyData, id=daily_data_id)

    # Get the batch ID to redirect to the correct page
    batch_id = daily_data_entry.batch_id  # Get the batch ID from the related batch

    daily_data_entry.delete()
    messages.success(request, "Daily data entry deleted successfully.")

    # Redirect to the list with the batch ID
    return redirect("list_daily_data", batch_id=batch_id)


def daily_feed_summary(request):
    current_batch = None
    past_batch = None
    compare_day = None
    current_feed_uplifted = 0
    current_weight_gain = 0
    current_water_consumption = 0  # New metric

    past_feed_uplifted = 0
    past_weight_gain = 0
    past_water_consumption = 0  # New metric

    feed_uplifted_percentage = 0
    weight_gain_percentage = 0
    water_consumption_percentage = 0  # New metric

    if request.method == "POST":
        form = DailyComparisonForm(request.POST, user=request.user)
        if form.is_valid():
            current_batch = form.cleaned_data["current_batch"]
            past_batch = form.cleaned_data["past_batch"]
            compare_day = int(form.cleaned_data["compare_day"])

            # Calculate the date for the selected day
            current_day_date = current_batch.batch_date + timedelta(
                days=compare_day - 1
            )
            past_day_date = past_batch.batch_date + timedelta(days=compare_day - 1)

            # Fetch the daily data
            current_day_data = DailyData.objects.filter(
                batch=current_batch, date=current_day_date
            ).first()
            past_day_data = DailyData.objects.filter(
                batch=past_batch, date=past_day_date
            ).first()

            # Extract data or set to 0 if not available
            current_feed_uplifted = (
                current_day_data.feed_uplifted if current_day_data else 0
            )
            current_weight_gain = (
                current_day_data.weight_gain if current_day_data else 0
            )
            current_water_consumption = (
                current_day_data.water_consumption if current_day_data else 0
            )

            past_feed_uplifted = past_day_data.feed_uplifted if past_day_data else 0
            past_weight_gain = past_day_data.weight_gain if past_day_data else 0
            past_water_consumption = (
                past_day_data.water_consumption if past_day_data else 0
            )

            # Calculate percentages (avoid division by zero)
            if current_feed_uplifted + past_feed_uplifted > 0:
                feed_uplifted_percentage = (
                    current_feed_uplifted / (current_feed_uplifted + past_feed_uplifted)
                ) * 100

            if current_weight_gain + past_weight_gain > 0:
                weight_gain_percentage = (
                    current_weight_gain / (current_weight_gain + past_weight_gain)
                ) * 100

            if current_water_consumption + past_water_consumption > 0:
                water_consumption_percentage = (
                    current_water_consumption
                    / (current_water_consumption + past_water_consumption)
                ) * 100

    else:
        form = DailyComparisonForm(user=request.user)

    return render(
        request,
        "daily_feed_summary.html",
        {
            "form": form,
            "current_batch": current_batch,
            "past_batch": past_batch,
            "compare_day": compare_day,
            "current_feed_uplifted": current_feed_uplifted,
            "current_weight_gain": current_weight_gain,
            "current_water_consumption": current_water_consumption,
            "past_feed_uplifted": past_feed_uplifted,
            "past_weight_gain": past_weight_gain,
            "past_water_consumption": past_water_consumption,
            "feed_uplifted_percentage": feed_uplifted_percentage,
            "weight_gain_percentage": weight_gain_percentage,
            "water_consumption_percentage": water_consumption_percentage,
        },
    )


def batch_feed_summary(request):
    if request.method == "POST":
        form = BatchSelectionForm(request.POST, user=request.user)
        if form.is_valid():
            selected_batch = form.cleaned_data["batch"]

            # Get daily data for the selected batch
            daily_data = DailyData.objects.filter(batch=selected_batch).order_by(
                "-date"
            )

            # Prepare data for the chart and table
            dates = [
                data.date.strftime("%Y-%m-%d") for data in daily_data
            ]  # Dates for the x-axis
            # Daily feed uplifted
            daily_feed_uplifted = [data.feed_uplifted for data in daily_data]
            # Weight gain per day
            total_weight_gain = [data.weight_gain for data in daily_data]

            # Calculate total feed used and total weight gain
            total_feed_used = sum(daily_feed_uplifted)
            total_weight_gain_sum = sum(total_weight_gain)

            # Prepare data for the table
            daily_data_for_table = zip(dates, daily_feed_uplifted, total_weight_gain)

            # Pass data to the template
            return render(
                request,
                "batch_feed_summary.html",
                {
                    "form": form,
                    "selected_batch": selected_batch,
                    "dates": dates,
                    "daily_feed_uplifted": daily_feed_uplifted,
                    "total_weight_gain": total_weight_gain,
                    "total_feed_used": total_feed_used,
                    "total_weight_gain": total_weight_gain_sum,
                    "daily_data": daily_data_for_table,  # Data for the table
                },
            )
    else:
        form = BatchSelectionForm(user=request.user)

    return render(request, "batch_feed_summary.html", {"form": form})


def feed_dashboard_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # For debugging purposes, you can print the user object to see if it's retrieved correctly
    print(f"User: {user.email}, ID: {user.id}")

    return render(request, "feed_dashboard.html", {"user": user})


def supplier_list(request):
    """Display the list of suppliers."""
    suppliers = Supplier.objects.all()  # Fetch all suppliers from the database
    return render(request, "supplier_list_stakeholder.html", {"suppliers": suppliers})


def tips(request):
    tips = WasteTip.objects.all()
    return render(request, "waste_management/tips.html", {"tips": tips})
@login_required

# views.py
def forum_dashboard(request, post_id=None):
    posts = Post.objects.all().order_by("-created_at")  # Fetch all posts
    
    selected_post = None
    comments = None
    
    # If a specific post is selected for chat
    if post_id:
        selected_post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=selected_post).order_by("created_at")
    
    if request.method == "POST":
        # Check if it's JSON data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                
                if "post_title" in data:  # Handle new post
                    title = data.get("post_title")
                    content = data.get("post_content")
                    category = data.get("post_category", "general")
                    
                    Post.objects.create(
                        title=title, 
                        content=content, 
                        owner=request.user,
                        category=category
                    )
                    return JsonResponse({"success": True})
                    
                elif "comment_content" in data:  # Handle new comment
                    content = data.get("comment_content")
                    Comment.objects.create(
                        content=content, 
                        post=selected_post, 
                        owner=request.user
                    )
                    return JsonResponse({"success": True})
                    
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
        
        # Handle form submissions (non-AJAX)
        else:
            if "post_title" in request.POST:  # Handle new post
                title = request.POST.get("post_title")
                content = request.POST.get("post_content")
                category = request.POST.get("post_category", "general")
                
                Post.objects.create(
                    title=title, 
                    content=content, 
                    owner=request.user,
                    category=category
                )
                return redirect("forum_dashboard")
                
            elif "comment_content" in request.POST:  # Handle new comment
                content = request.POST.get("comment_content")
                Comment.objects.create(
                    content=content, 
                    post=selected_post, 
                    owner=request.user
                )
                return redirect("forum_dashboard", post_id=post_id)
    
    # Fix the context to include all necessary data
    context = {
        "posts": posts,
        "selected_post": selected_post,
        "comments": comments,
        "current_category": request.GET.get('category', 'all'),
        "category_counts": {
            "all": posts.count(),
            "fcr": posts.filter(category='fcr').count(),
            "health": posts.filter(category='health').count(),
            "best_practices": posts.filter(category='best_practices').count(),
        }
    }
    
    # Return the correct context
    return render(request, "forum/forum_dashboard.html", context)




# views.py
from django.shortcuts import render

def chat_room(request, stakeholder_id=None):
    """Handle chat room view"""
    context = {
        'room_name': stakeholder_id or 'general',
        'stakeholder_id': stakeholder_id
    }
    return render(request, 'chat_room.html', context)

def send_message(request):
    """Handle sending chat messages"""
    if request.method == 'POST':
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def get_messages(request, room_id):
    """Get chat messages for a room"""
    return JsonResponse({'messages': []})

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, owner=request.user)
    post.delete()
    return redirect('forum_dashboard')



from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json


@login_required
@csrf_protect
@require_http_methods(["POST"])
def chat_api(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').lower()
        context = data.get('context', {})
        farm_id = data.get('farm_id')

        # Get farm data
        farm = Farm.objects.get(id=farm_id)
        
        # Basic response logic based on message content
        if 'fcr' in message:
            current_fcr = float(context.get('fcr', 0))
            if current_fcr > 0:
                if current_fcr <= 1.5:
                    response = f"Your FCR of {current_fcr} is excellent! Keep up the good work. To maintain this performance, ensure consistent feed quality and maintain optimal temperature conditions."
                elif current_fcr <= 1.8:
                    response = f"Your FCR of {current_fcr} is good but has room for improvement. Consider reviewing your feeding schedule and environmental controls."
                else:
                    response = f"Your FCR of {current_fcr} needs attention. I recommend checking feed quality, reducing waste, and optimizing temperature conditions. Would you like specific recommendations?"
            else:
                response = "I don't have enough FCR data yet. Please ensure your records are up to date."

        elif any(word in message for word in ['incentive', 'bonus', 'payment']):
            # Calculate incentives based on performance
            fcr = float(context.get('fcr', 0))
            if fcr > 0:
                bonus = calculate_incentive(fcr)
                response = f"Based on your FCR of {fcr}, you're eligible for a {bonus}% bonus. Keep improving to earn more!"
            else:
                response = "I can't calculate incentives without FCR data. Please update your records."

        elif any(word in message for word in ['problem', 'issue', 'help', 'trouble']):
            response = "I can help troubleshoot common issues. Please specify if you're having problems with:\n- Feed consumption\n- Growth rate\n- Disease concerns\n- Environmental controls"

        elif 'sustainability' in message:
            response = "Here are some sustainability practices you can implement:\n1. Optimize ventilation to reduce energy use\n2. Implement water conservation measures\n3. Consider solar panels for energy needs\n4. Use organic waste for composting\nWould you like more details about any of these?"

        else:
            response = "I can help you with FCR analysis, incentive programs, troubleshooting, and sustainability practices. What would you like to know more about?"

        return JsonResponse({
            'response': response,
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def calculate_incentive(fcr):
    """Calculate bonus percentage based on FCR"""
    if fcr <= 1.5:
        return 10
    elif fcr <= 1.7:
        return 7
    elif fcr <= 1.9:
        return 5
    return 0
from django.shortcuts import render
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os

from django.shortcuts import render
from django.contrib import messages

# @login_required
# @login_required
# def chick_health_recognition(request):
#     """View for disease prediction"""
#     batches = ChickBatch.objects.filter(batch_status='active').order_by('-batch_date')
    
#     if request.method == 'POST' and request.FILES.get('chick_image'):
#         try:
#             image_file = request.FILES['chick_image']
#             batch_id = request.POST.get('batch_id')
            
#             # Ensure batch_id is provided
#             if not batch_id:
#                 messages.error(request, 'Please select a batch')
#                 return redirect('chick_health_recognition')

#             # Fetch the batch safely
#             selected_batch = ChickBatch.objects.filter(id=batch_id).first()
#             if not selected_batch:
#                 messages.error(request, f'Batch with ID {batch_id} not found.')
#                 return redirect('chick_health_recognition')

#             # Process the image file directly
#             result = predict_disease(image_file)
#             print(f"🔍 Debug Output from predict_disease: {result}")  # ✅ Debugging step
            
#             # Ensure result is a dictionary
#             if isinstance(result, dict) and "disease" in result and "confidence" in result:
#                 predicted_class = result["disease"]
#                 confidence_score = float(result["confidence"].strip('%'))  # Convert to float
#                 symptoms_detected = result.get("symptoms", [])  # Get symptoms if available
#                 severity = result.get("severity", "Unknown")  # Default to "Unknown" if missing
#             else:
#                 raise ValueError(f"Unexpected return value from predict_disease: {result}")

#             # Save the analysis
#             analysis = DiseaseAnalysis.objects.create(
#                 image=image_file,
#                 predicted_disease=predicted_class,
#                 confidence_score=confidence_score,
#                 symptoms_detected=symptoms_detected,
#                 batch=selected_batch,
#                 created_by=request.user
#             )
            
#             messages.success(request, 'Analysis completed successfully!')
#             return redirect('disease_analysis_detail', analysis_id=analysis.id)
            
#         except Exception as e:
#             messages.error(request, f'Error processing image: {str(e)}')
#             return redirect('chick_health_recognition')
    
#     context = {
#         'batches': batches,
#         'recent_analyses': DiseaseAnalysis.objects.all().order_by('-analyzed_date')[:5]
#     }
    
#     return render(request, 'chick_health_recognition.html', context)




# def get_disease_symptoms(disease):
#     """Return common symptoms for each disease"""
#     symptoms_map = {
#         'healthy': [],
#         'coccidiosis': ['Bloody droppings', 'Lethargy', 'Ruffled feathers'],
#         'new castle disease': ['Respiratory distress', 'Nervous symptoms', 'Drop in egg production'],
#         'salmonella': ['Diarrhea', 'Loss of appetite', 'Depression']
#     }
#     return symptoms_map.get(disease.lower(), [])

# @login_required
# def disease_analysis_list(request):
#     """View to display list of disease analyses"""
#     analyses = DiseaseAnalysis.objects.filter(
#         batch__user=request.user
#     ).order_by('-analyzed_date')
    
#     return render(request, 'stakeholder/disease_analysis_list.html', {
#         'analyses': analyses
#     })

# @login_required
# def disease_analysis_detail(request, analysis_id):
#     """View to display details of a specific analysis"""
#     analysis = get_object_or_404(DiseaseAnalysis, 
#                                 id=analysis_id, 
#                                 batch__user=request.user)
    
#     return render(request, 'stakeholder/disease_analysis_detail.html', {
#         'analysis': analysis
#     })

# def load_disease_model():
#     """Load the trained disease detection model"""
#     try:
#         model_path = os.path.join(settings.BASE_DIR, 'stakeholder', 'models', 'poultry_disease_classifier_retrained.h5')
        
#         if os.path.exists(model_path):
#             # Load model with custom metrics if used during training
#             model = tf.keras.models.load_model(model_path, compile=False)
            
#             # Compile with same settings as training
#             model.compile(
#                 optimizer='adam',
#                 loss='categorical_crossentropy',
#                 metrics=['accuracy']
#             )
#             print(f"Model loaded successfully from {model_path}")
#             return model
#         else:
#             print(f"Model file not found at {model_path}")
#             return None
            
#     except Exception as e:
#         print(f"Error loading model: {str(e)}")
#         return None

# # Load model once when module is imported
# model = load_disease_model()

# @login_required
# def provide_feedback(request, analysis_id):
#     """Handle feedback for model predictions"""
#     analysis = get_object_or_404(DiseaseAnalysis, id=analysis_id, batch__user=request.user)
    
#     if request.method == 'POST':
#         correct_label = request.POST.get('correct_label')
        
#         if correct_label:
#             # Update the analysis with feedback
#             analysis.predicted_disease = correct_label
#             analysis.save()
            
#             messages.success(request, "Thank you for your feedback!")
#         else:
#             messages.error(request, "Please provide a correct label")
            
#     return redirect('disease_analysis_detail', analysis_id=analysis_id)

# @login_required
# def batch_detail_qr(request, batch_uuid):
#     """View batch details via QR code"""
#     batch = get_object_or_404(ChickBatch, batch_uuid=batch_uuid)
    
#     # Get all analyses for this batch
#     analyses = DiseaseAnalysis.objects.filter(batch=batch).order_by('-analyzed_date')
    
#     # Get daily data
#     daily_data = DailyData.objects.filter(batch=batch).order_by('-date')
    
#     # Calculate key metrics
#     mortality_data = daily_data.aggregate(
#         total_mortality=Sum('mortality_count'),
#         avg_weight=Avg('weight_gain')
#     )
    
#     # Calculate FCR if possible
#     total_feed = daily_data.aggregate(total_feed=Sum('feed_consumed'))['total_feed'] or 0
#     total_weight_gain = daily_data.aggregate(total_gain=Sum('weight_gain'))['total_gain'] or 0
#     fcr = total_feed / total_weight_gain if total_weight_gain > 0 else 0
    
#     context = {
#         'batch': batch,
#         'analyses': analyses,
#         'daily_data': daily_data,
#         'total_mortality': mortality_data['total_mortality'] or 0,
#         'avg_weight': mortality_data['avg_weight'] or 0,
#         'age_days': (timezone.now().date() - batch.batch_date).days,
#         'batch_type': batch.batch_type,
#         'initial_count': batch.initial_chick_count,
#         'current_count': batch.live_chick_count,
#         'batch_status': batch.batch_status,
#         'duration': batch.duration,
#         'fcr': round(fcr, 2) if fcr else 0,
#         'total_feed': total_feed,
#         'total_weight_gain': total_weight_gain
#     }
    
#     return render(request, 'stakeholder/batch_detail_qr.html', context)
from django.shortcuts import render, get_object_or_404
from stakeholder.models import ChickBatch
from django.conf import settings

def batch_detail_qr(request, batch_uuid):
    """View batch details via QR code"""
    batch = get_object_or_404(ChickBatch, batch_uuid=batch_uuid)
    
    context = {
        'batch': batch,
        'batch_uuid': batch_uuid,  # Include batch_uuid for debugging
        'MEDIA_URL': settings.MEDIA_URL,  # Ensure MEDIA_URL is available
    }
    
    return render(request, 'stakeholder/batch_detail_qr.html', context)


@login_required
def view_batch_qrcodes(request):
    batches = ChickBatch.objects.all()
    context = {
        'batches': batches,
        'is_admin': request.user.is_staff,
        'debug': settings.DEBUG,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'stakeholder/view_batch_qrcodes.html', context)

def test_media(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'batch_qr_codes', filename)
    print(f"\nTest Media Debug:")
    print(f"Requested filename: {filename}")
    print(f"Full file path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"Media root: {settings.MEDIA_ROOT}")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                response = FileResponse(f, content_type='image/png')
                print("File opened successfully")
                return response
        except Exception as e:
            print(f"Error opening file: {str(e)}")
            return HttpResponse(f"Error opening file: {str(e)}", status=500)
    else:
        print(f"File not found at path: {file_path}")
        # List contents of the directory
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'batch_qr_codes')
        if os.path.exists(qr_dir):
            print("\nDirectory contents:")
            for file in os.listdir(qr_dir):
                print(f"- {file}")
        return HttpResponse(f"File not found: {file_path}", status=404)
from .forms import FeedStockForm  # Add this import

@login_required
def feed_main_dashboard(request):
    # Get feed stocks
    feed_stocks = FeedStock.objects.all()
    form = FeedStockForm()

    # Get recent feed acknowledgments for the last 7 days
    feed_notifications = FeedNotification.objects.filter(
        notification_type='acknowledgment',
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).select_related('batch', 'feed_assignment').order_by('-created_at')

    # Get pending assignments count
    pending_assignments = FeedAssignment.objects.filter(status='pending').count()

    # Get active batches count
    active_batches_count = ChickBatch.objects.filter(batch_status='active').count()

    # Prepare feed type statistics
    feed_type_stats = {
        'starter': FeedStock.objects.filter(feed_type='starter').aggregate(total=Sum('number_of_sacks'))['total'] or 0,
        'grower': FeedStock.objects.filter(feed_type='grower').aggregate(total=Sum('number_of_sacks'))['total'] or 0,
        'finisher': FeedStock.objects.filter(feed_type='finisher').aggregate(total=Sum('number_of_sacks'))['total'] or 0,
    }

    context = {
        'feed_stocks': feed_stocks,
        'form': form,
        'is_admin': request.user.is_staff,
        'feed_acknowledgments': feed_notifications,
        'pending_assignments': pending_assignments,
        'active_batches_count': active_batches_count,
        'feed_type_stats': feed_type_stats,
        'notifications_count': feed_notifications.count(),
    }
    return render(request, 'stakeholder/feed_main_dashboard.html', context)

@login_required
def add_feed_stock(request):
    if not request.user.is_staff:
        messages.error(request, 'Only admin can add feed stock')
        return redirect('feed_main_dashboard')
        
    if request.method == 'POST':
        form = FeedStockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feed stock added successfully')
            return redirect('feed_main_dashboard')
    else:
        form = FeedStockForm()  # Initialize an empty form for GET requests

    return render(request, 'stakeholder/feed_form.html', {'form': form})
@login_required
def feed_stock_create(request):
    """Create new feed stock"""
    if not request.user.is_staff:
        messages.error(request, 'Only admin can add feed stock')
        return redirect('feed_manage')
        
    if request.method == 'POST':
        try:
            # Get form data
            feed_type = request.POST.get('feed_type')
            number_of_sacks = int(request.POST.get('number_of_sacks'))
            price_per_sack = Decimal(request.POST.get('price_per_sack'))
            minimum_sacks = int(request.POST.get('minimum_sacks'))
            
            # Create new feed stock
            FeedStock.objects.create(
                feed_type=feed_type,
                number_of_sacks=number_of_sacks,
                price_per_sack=price_per_sack,
                minimum_sacks=minimum_sacks
            )
            
            messages.success(request, 'Feed stock added successfully')
            
        except ValueError as e:
            messages.error(request, f'Invalid value: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error creating feed stock: {str(e)}')
            
    return redirect('feed_manage')
def update_feed_stock(request, feed_id):
    """Update feed stock"""
    if request.method == 'POST':
        try:
            feed_stock = get_object_or_404(FeedStock, id=feed_id)
            
            # Update the feed stock with form data
            feed_stock.feed_type = request.POST.get('feed_type')
            feed_stock.number_of_sacks = int(request.POST.get('number_of_sacks'))
            feed_stock.price_per_sack = Decimal(request.POST.get('price_per_sack'))
            feed_stock.minimum_sacks = int(request.POST.get('minimum_sacks'))
            feed_stock.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully updated {feed_stock.get_feed_type_display()}'
                })
            
            messages.success(request, f'Successfully updated {feed_stock.get_feed_type_display()}')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
            
            messages.error(request, f'Error updating feed stock: {str(e)}')
    
    return redirect('feed_manage')
def delete_feed_stock(request, feed_id):
    if request.method == "POST":
        feed_stock = get_object_or_404(FeedStock, id=feed_id)
        feed_stock.delete()
        messages.success(request, "Feed stock deleted successfully.")
    return redirect('feed_manage')  # Change this to your feed management view name
    
@login_required
def feed_manage(request):
    """Feed management view"""
    feed_stocks = FeedStock.objects.all()

    if request.method == 'POST':
        # Check if it's a delete request
        if 'delete' in request.POST:
            return redirect('feed_manage')
            
        # Handle add/edit form
        form = FeedStockForm(request.POST)
        if form.is_valid():
            try:
                feed_stock = form.save()
                messages.success(request, 'Feed stock added successfully!')
                return redirect('feed_manage')
            except Exception as e:
                messages.error(request, f'Error saving feed stock: {str(e)}')
        else:
            # Print form errors to console for debugging
            print("Form errors:", form.errors)
            error_messages = []
            for field, errors in form.errors.items():
                error_messages.append(f"{field}: {', '.join(errors)}")
            messages.error(request, f"Error in form: {'; '.join(error_messages)}")
    else:
        form = FeedStockForm()

    context = {
        'feed_stocks': feed_stocks,
        'form': form,
        'title': 'Feed Management'
    }
    return render(request, 'stakeholder/feed_manage.html', context)



@login_required
def feed_stock_create(request):
       """Create new feed stock"""
       if request.method == 'POST':
           form = FeedStockForm(request.POST)
           if form.is_valid():
               form.save()
               messages.success(request, 'Feed stock created successfully!')
               return redirect('feed_manage')
           else:
               messages.error(request, 'Error creating feed stock. Please check the form.')
       else:
           form = FeedStockForm()

       context = {
           'form': form,
           'title': 'Add New Feed Stock'
       }
       return render(request, 'stakeholder/feed_manage.html', context)




@login_required
def feed_dashboard(request):
    # Get all feed stocks
    feed_stocks = FeedStock.objects.all()
    
    # Calculate stock by feed type
    starter_feed = feed_stocks.filter(feed_type='starter').first()
    grower_feed = feed_stocks.filter(feed_type='grower').first()
    finisher_feed = feed_stocks.filter(feed_type='finisher').first()
    
    context = {
        'feed_stocks': feed_stocks,
        'starter_feed': starter_feed,
        'grower_feed': grower_feed,
        'finisher_feed': finisher_feed,
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'stakeholder/feed_dashboard.html', context)

@require_http_methods(["GET"])
def calculate_feed(request, chick_count):
    try:
        # Calculate feed requirements
        calculations = FeedCalculator.calculate_feed_requirements(chick_count)
        return JsonResponse(calculations)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def update_feed(request):
    """Update existing feed stock"""
    if request.method == 'POST':
        feed_id = request.POST.get('feed_id')
        add_sacks = int(request.POST.get('add_sacks'))
        new_price = Decimal(request.POST.get('price_per_sack'))
        
        try:
            feed_stock = get_object_or_404(FeedStock, id=feed_id)
            feed_stock.number_of_sacks += add_sacks
            feed_stock.price_per_sack = new_price
            feed_stock.save()
            messages.success(request, f'Successfully updated {feed_stock.feed_type} stock')
        except Exception as e:
            messages.error(request, f'Error updating feed stock: {str(e)}')
            
    return redirect('feed_manage')






@login_required


def view_stakeholder_view(request, id):
    user = get_object_or_404(User, id=id)
    batches = ChickBatch.objects.filter(user=user).order_by('-batch_date')
    
    # Calculate feed statistics for each batch
    for batch in batches:
        batch.feed_stats = {
            'total_assigned': batch.total_feed_sacks,
            'starter_assigned': batch.starter_feed_sacks,
            'remaining': batch.remaining_feed_sacks,
        }
    
    context = {
        'user': user,
        'batches': batches,
    }
    
    return render(request, 'stakeholder.html', context)






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import ChickBatch, FeedAssignment
from user.models import FeedStock

@login_required
def active_batches_feed(request):
    """View for managing feed assignments for active batches"""
    batches = ChickBatch.objects.filter(batch_status='active')
    batch_feed_data = []

    for batch in batches:
        # Calculate current week
        days_since_start = (timezone.now().date() - batch.batch_date).days
        current_week = min((days_since_start // 7) + 1, 6)
        
        # Get feed history and assigned weeks
        feed_history = FeedAssignment.objects.filter(batch=batch).order_by('week_number')
        assigned_weeks = feed_history.values_list('week_number', flat=True)
        
        # Find next unassigned week
        next_week = None
        for week in range(1, min(current_week + 1, 7)):
            if week not in assigned_weeks:
                next_week = week
                break

        # Check if week transition happened
        last_assigned_week = max(assigned_weeks) if assigned_weeks else 0
        week_changed = current_week > last_assigned_week and current_week <= 6

        # Determine feed type based on next week
        if next_week and next_week <= 3:
            feed_type = 'starter'
        elif next_week and next_week <= 5:
            feed_type = 'grower'
        else:
            feed_type = 'finisher'

        batch_data = {
            'batch': batch,
            'current_week': current_week,
            'next_week': next_week,
            'week_changed': week_changed,
            'last_assigned_week': last_assigned_week,
            'feed_type': dict(FeedStock.FEED_TYPE_CHOICES)[feed_type],
            'available_feed_stocks': FeedStock.objects.filter(
                feed_type=feed_type, 
                number_of_sacks__gt=0
            ),
            'assigned_weeks': assigned_weeks,
            'can_assign': next_week is not None,
            'recommended_sacks': calculate_recommended_sacks(batch, next_week or current_week),
            'feed_history': feed_history,
            'total_assigned': feed_history.aggregate(total=Sum('sacks_assigned'))['total'] or 0,
        }
        batch_feed_data.append(batch_data)

    return render(request, 'stakeholder/active_batch_feed.html', {'batch_feed_data': batch_feed_data})

@login_required
@transaction.atomic
def batch_feed_assignment(request, batch_id):
    """Handle feed assignment for a specific batch"""
    batch = get_object_or_404(ChickBatch, id=batch_id)
    
    if request.method == 'POST':
        try:
            week_number = int(request.POST.get('week_number'))
            sacks_assigned = int(request.POST.get('sacks_assigned'))
            feed_stock_id = request.POST.get('feed_stock')
            
            # Calculate current week
            days_since_start = (timezone.now().date() - batch.batch_date).days
            current_week = min((days_since_start // 7) + 1, 6)
            is_late = week_number < current_week
            
            # Get and update feed stock
            feed_stock = get_object_or_404(FeedStock, id=feed_stock_id)
            if feed_stock.number_of_sacks < sacks_assigned:
                raise ValueError(f"Not enough feed stock available. Requested: {sacks_assigned}, Available: {feed_stock.number_of_sacks}")
            
            feed_stock.number_of_sacks -= sacks_assigned
            feed_stock.save()
            
            # Create feed assignment
            assignment = FeedAssignment.objects.create(
                batch=batch,
                week_number=week_number,
                sacks_assigned=sacks_assigned,
                cost_per_sack=feed_stock.price_per_sack,
                is_late=is_late,
                assigned_date=timezone.now(),
                feed_stock=feed_stock  # Add this line
            )
            
            msg = f'Successfully assigned {sacks_assigned} sacks for Week {week_number}'
            if is_late:
                msg += ' (Late Assignment)'
            messages.success(request, msg)
            
        except Exception as e:
            messages.error(request, f"Error assigning feed: {str(e)}")
    
    return redirect('active_batches_feed')

@login_required
def daily_feed_report(request, date):
    try:
        # Convert string date to datetime
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get all feed assignments for the date (use date range for full day)
        assignments = FeedAssignment.objects.filter(
            assigned_date__date=report_date
        ).select_related('batch', 'batch__farm', 'feed_stock')
        
        print(f"Debug - Report Date: {report_date}")
        print(f"Debug - Found Assignments: {assignments.count()}")
        
        # Calculate totals
        total_assignments = assignments.count()
        total_sacks = sum(a.sacks_assigned for a in assignments)
        total_cost = sum(a.sacks_assigned * a.cost_per_sack for a in assignments)
        
        # Add calculated fields to assignments
        for assignment in assignments:
            assignment.total_cost = assignment.sacks_assigned * assignment.cost_per_sack
        
        context = {
            'report_date': report_date,
            'assignments': assignments,
            'summary': {
                'total_assignments': total_assignments,
                'total_sacks': total_sacks,
                'total_cost': total_cost,
                'active_batches': assignments.values('batch').distinct().count()
            },
            'company_name': 'Feather Farm Solutions',
            'generated_at': timezone.now()
        }
        
        template = get_template('stakeholder/feed_report_pdf.html')
        html = template.render(context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename=feed_report_{date}.pdf'
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
            
        return response
        
    except ValueError as e:
        print(f"Debug - ValueError: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f"Invalid date format: {str(e)}"
        }, status=400)
    except Exception as e:
        print(f"Debug - Error occurred: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def export_daily_report(request, date):
    try:
        # Convert string date to datetime
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get all feed assignments for the date
        assignments = FeedAssignment.objects.filter(
            assigned_date__date=report_date
        ).select_related('batch', 'batch__farm')
        
        # Create the response with CSV headers
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="feed_report_{date}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write headers
        writer.writerow([
            'Time',
            'Batch ID',
            'Farm Name',
            'Feed Type',
            'Week Number',
            'Sacks Assigned',
            'Cost per Sack',
            'Total Cost'
        ])
        
        # Write data rows
        for assignment in assignments:
            writer.writerow([
                assignment.assigned_date.strftime('%H:%M'),
                assignment.batch.id,
                assignment.batch.farm.name,
                assignment.get_feed_type_display(),
                f'Week {assignment.week_number}',
                assignment.sacks_assigned,
                f'₹{assignment.cost_per_sack}',
                f'₹{assignment.total_cost}'
            ])
            
        return response
        
    except ValueError:
        messages.error(request, "Invalid date format. Use YYYY-MM-DD")
        return redirect('feed_dashboard')
    except Exception as e:
        messages.error(request, f"Error exporting report: {str(e)}")
        return redirect('feed_dashboard')

@login_required
def generate_feed_report_pdf(request, date):
    try:
        # Convert string date to datetime
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get all feed assignments for the date
        assignments = FeedAssignment.objects.filter(
            assigned_date__date=report_date
        ).select_related('batch', 'batch__farm')
        
        # Calculate summary statistics
        total_assignments = assignments.count()
        active_batches = assignments.values('batch').distinct().count()
        total_sacks = assignments.aggregate(total=Sum('sacks_assigned'))['total'] or 0
        total_cost = assignments.aggregate(
            total=Sum(F('sacks_assigned') * F('cost_per_sack'))
        )['total'] or 0
        
        # Prepare context for PDF template
        context = {
            'report_date': report_date,
            'assignments': assignments,
            'total_assignments': total_assignments,
            'active_batches': active_batches,
            'total_sacks': total_sacks,
            'total_cost': total_cost,
            'company_name': 'Feather Farm Solutions',
            'generated_at': timezone.now()
        }
        
        # Get the template
        template = get_template('stakeholder/feed_report_pdf.html')
        html = template.render(context)
        
        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="feed_report_{date}.pdf"'
        
        # Create PDF
        pisa_status = pisa.CreatePDF(
            html,
            dest=response,
            encoding='utf-8'
        )
        
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
            
        return response
        
    except ValueError:
        messages.error(request, "Invalid date format. Use YYYY-MM-DD")
        return redirect('feed_dashboard')
    except Exception as e:
        messages.error(request, f"Error generating PDF report: {str(e)}")
        return redirect('feed_dashboard')


@login_required
def list_daily_feed(request, batch_id):
    try:
        # Get the batch and verify ownership
        batch = get_object_or_404(ChickBatch, id=batch_id)
        if batch.user != request.user:
            messages.error(request, "You don't have permission to view this batch's feed records.")
            return redirect('stateholder_batch')
            
        # Get all feed consumption records for this batch
        feed_records = DailyFeedConsumption.objects.filter(
            batch=batch
        ).select_related(
            'feed_assignment',
            'recorded_by'
        ).order_by('-date')
        
        context = {
            'batch': batch,
            'feed_records': feed_records,
        }
        
        return render(request, 'stakeholder/list_daily_feed.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading feed records: {str(e)}")
        return redirect('stateholder_batch')

@login_required
def get_batch_feed_assignments(request, batch_id):
    try:
        batch = get_object_or_404(ChickBatch, id=batch_id)
        
        # Get all feed assignments for this batch
        assignments = FeedAssignment.objects.filter(batch=batch).order_by('-assigned_date')
        
        # Prepare data for JSON response
        assignments_data = []
        for assignment in assignments:
            assignments_data.append({
                'id': assignment.id,
                'feed_type': assignment.get_feed_type_display(),
                'week_number': assignment.week_number,
                'sacks_assigned': assignment.sacks_assigned,
                'sacks_remaining': assignment.remaining_sacks,
                'cost_per_sack': float(assignment.cost_per_sack),
                'total_cost': float(assignment.total_cost),
                'assigned_date': assignment.assigned_date.strftime('%Y-%m-%d %H:%M'),
                'status': assignment.status,
                'record_url': reverse('record_feed_consumption', kwargs={
                    'batch_id': batch.id,
                    'assignment_id': assignment.id
                })
            })
        
        return JsonResponse({
            'success': True,
            'assignments': assignments_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from user.models import FeedStock



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import ChickBatch, FeedAssignment,FeedNotification
from user.models import FeedStock

@login_required
def feed_tracking_dashboard(request):
    # Add debug print statements
    try:
        template = get_template('stakeholder/feed_tracking1.html')
        print(f"Template found at: {template.origin.name}")  # This will print the template path
    except TemplateDoesNotExist as e:
        print(f"Template not found: {str(e)}")

    # Get active batches for the stakeholder
    active_batches = ChickBatch.objects.filter(
        user=request.user,
        batch_status='active'
    ).select_related(
        'farm'
    ).prefetch_related(
        'feed_assignments',
        'daily_feed_records'
    )

    context = {
        'active_batches': active_batches,
        'page_title': 'Feed Tracking'
    }
    
    print("Rendering template with context:", context.keys())  # Debug print
    return render(request, 'stakeholder/feed_tracking1.html', context)



@login_required
def acknowledge_feed_assignment(request, assignment_id):
    if request.method == 'POST':
        try:
            assignment = get_object_or_404(FeedAssignment, id=assignment_id)
            action = request.POST.get('action')
            notes = request.POST.get('notes', '')

            if action == 'acknowledge':
                assignment.status = 'acknowledged'
                message = 'Feed assignment acknowledged successfully'
            elif action == 'reject':
                assignment.status = 'rejected'
                message = 'Feed assignment rejected successfully'
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid action'
                })

            assignment.acknowledgment_date = timezone.now()
            assignment.acknowledgment_notes = notes
            assignment.save()

            # Create notification
            FeedNotification.objects.create(
                batch=assignment.batch,
                feed_assignment=assignment,
                notification_type='acknowledgment',
                status=action,
                notes=notes
            )

            return JsonResponse({
                'status': 'success',
                'message': message
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })







@login_required
@require_http_methods(["GET"])
def get_vaccine_details(request, vaccine_id):
    try:
        vaccine = Vaccine.objects.get(id=vaccine_id)
        return JsonResponse({
            'success': True,
            'vaccine': {
                'name': vaccine.name,
                'manufacturer': vaccine.manufacturer,
                'vaccination_day': vaccine.vaccination_day,
                'current_stock': vaccine.current_stock,
                'minimum_stock_level': vaccine.minimum_stock_level
            }
        })
    except Vaccine.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Vaccine not found'
        }, status=404)

def validate_vaccine_data(data):
    errors = []
    
    # Name validation
    name = data.get('name', '').strip()
    if not name:
        errors.append('Name is required')
    elif len(name) > 100:
        errors.append('Name must be less than 100 characters')
    elif not name.isalnum():
        errors.append('Name should only contain letters and numbers')
    
    # Manufacturer validation
    manufacturer = data.get('manufacturer', '').strip()
    if not manufacturer:
        errors.append('Manufacturer is required')
    elif len(manufacturer) > 100:
        errors.append('Manufacturer must be less than 100 characters')
    
    # Vaccination day validation
    try:
        vaccination_day = int(data.get('vaccination_day', ''))
        if vaccination_day not in [7, 14, 21]:
            errors.append('Invalid vaccination day. Must be 7, 14, or 21')
    except ValueError:
        errors.append('Vaccination day must be a number')
    
    # Stock validation
    try:
        current_stock = int(data.get('current_stock', '0'))
        if current_stock < 0:
            errors.append('Current stock cannot be negative')
    except ValueError:
        errors.append('Current stock must be a number')
    
    try:
        minimum_stock = int(data.get('minimum_stock_level', '0'))
        if minimum_stock < 0:
            errors.append('Minimum stock level cannot be negative')
    except ValueError:
        errors.append('Minimum stock level must be a number')
    
    # Doses validation
    try:
        doses_required = int(data.get('doses_required', '1'))
        if doses_required < 1:
            errors.append('Doses required must be at least 1')
    except ValueError:
        errors.append('Doses required must be a number')
    
    try:
        interval_days = int(data.get('interval_days', '0'))
        if interval_days < 0:
            errors.append('Interval days cannot be negative')
    except ValueError:
        errors.append('Interval days must be a number')
    
    return errors

@login_required
def add_vaccine(request):
    if request.method == 'POST':
        # Validate the data
        errors = validate_vaccine_data(request.POST)
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation errors: ' + ', '.join(errors)
            }, status=400)
        
        try:
            # Create vaccine with validated data
            vaccine = Vaccine.objects.create(
                name=request.POST.get('name').strip(),
                manufacturer=request.POST.get('manufacturer').strip(),
                vaccination_day=int(request.POST.get('vaccination_day')),
                current_stock=int(request.POST.get('current_stock', 0)),
                minimum_stock_level=int(request.POST.get('minimum_stock_level', 10)),
                doses_required=int(request.POST.get('doses_required', 1)),
                interval_days=int(request.POST.get('interval_days', 0))
            )
            
            # Update stock status
            if vaccine.current_stock <= 0:
                vaccine.stock_status = 'OUT_OF_STOCK'
            elif vaccine.current_stock <= vaccine.minimum_stock_level:
                vaccine.stock_status = 'LOW_STOCK'
            else:
                vaccine.stock_status = 'IN_STOCK'
            
            vaccine.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Vaccine added successfully'
            })
        except Exception as e:
            print(f"Error adding vaccine: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)

@login_required
def update_vaccine(request, vaccine_id):
    if request.method == 'POST':
        # Validate the data
        errors = validate_vaccine_data(request.POST)
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation errors: ' + ', '.join(errors)
            }, status=400)
        
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
            
            # Update with validated data
            vaccine.name = request.POST.get('name').strip()
            vaccine.manufacturer = request.POST.get('manufacturer').strip()
            vaccine.vaccination_day = int(request.POST.get('vaccination_day'))
            vaccine.current_stock = int(request.POST.get('current_stock'))
            vaccine.minimum_stock_level = int(request.POST.get('minimum_stock_level'))
            vaccine.doses_required = int(request.POST.get('doses_required', 1))
            vaccine.interval_days = int(request.POST.get('interval_days', 0))
            
            # Update stock status
            if vaccine.current_stock <= 0:
                vaccine.stock_status = 'OUT_OF_STOCK'
            elif vaccine.current_stock <= vaccine.minimum_stock_level:
                vaccine.stock_status = 'LOW_STOCK'
            else:
                vaccine.stock_status = 'IN_STOCK'
            
            vaccine.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Vaccine updated successfully'
            })
        except Vaccine.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Vaccine not found'
            }, status=404)
        except Exception as e:
            print(f"Error updating vaccine: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@login_required
@require_http_methods(["POST"])
def delete_vaccine(request, vaccine_id):
    if request.method == 'POST':
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
            vaccine.delete()
            return JsonResponse({
                'success': True,
                'message': 'Vaccine deleted successfully'
            })
        except Vaccine.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Vaccine not found'
            }, status=404)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@login_required
def manage_vaccines(request):
    vaccines = Vaccine.objects.all().order_by('vaccination_day')
    print(f"Number of vaccines found: {vaccines.count()}")
    for vaccine in vaccines:
        print(f"Vaccine: {vaccine.name}, Day: {vaccine.vaccination_day}")
    
    context = {
        'vaccines': vaccines,
        'page_title': 'Manage Vaccines',
        'debug': True  # Add this for template debugging
    }
    
    return render(request, 'manage_vaccines.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from django.http import JsonResponse
from django.db.models import F
from .models import ChickBatch, VaccinationSchedule  # Add this import
from user.models import Vaccine  # Add this import

@login_required
def assign_vaccination(request):
    batch_id = request.GET.get('batch_id')
    vaccination_day = request.GET.get('vaccination_day')
    
    try:
        batch = ChickBatch.objects.get(id=batch_id)
        vaccine = Vaccine.objects.filter(vaccination_day=vaccination_day).first()
        
        context = {
            'batch': batch,
            'vaccine': vaccine,
            'vaccination_day': vaccination_day,
        }
        
        if request.method == 'POST':
            # Convert vaccination_date string to datetime
            vaccination_date_str = request.POST.get('vaccination_date')
            try:
                vaccination_date = datetime.strptime(vaccination_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                vaccination_date = batch.batch_date + timezone.timedelta(days=int(vaccination_day))

            # Create vaccination schedule
            vaccination = VaccinationSchedule.objects.create(
                batch=batch,
                vaccine=vaccine,
                vaccination_date=vaccination_date,
                notes=request.POST.get('notes', ''),
                farm_coordinates=f"{batch.farm.latitude},{batch.farm.longitude}"  # Add this line
            )
            
            # QR code will be automatically generated in the save method
            
            # Prepare email
            subject = f'Vaccination Schedule - Day {vaccination_day}'
            email_context = {
                'batch': batch,
                'vaccine': vaccine,
                'vaccination_date': vaccination_date,
            }
            
            html_message = render_to_string('stakeholder/email/vaccination_schedule.html', email_context)

            # Get the farm owner's email
            if batch.farm:
                recipient_email = batch.farm.owner.email
            else:
                messages.warning(request, 'No farm owner found, sending email to assigning user')
                recipient_email = request.user.email

            # Send email
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[recipient_email],
            )
            email.content_subtype = 'html'
            try:
                email.send()
                messages.success(request, f'Vaccination scheduled successfully and notification sent to {recipient_email}')
            except Exception as e:
                messages.warning(request, f'Vaccination scheduled but email could not be sent: {str(e)}')

            return redirect('vaccination_list')
            
        return render(request, 'assign_vaccination.html', context)
        
    except (ChickBatch.DoesNotExist, Vaccine.DoesNotExist) as e:
        messages.error(request, str(e))
        return redirect('vaccination_main')

@login_required
def vaccination_main(request):
    try:
        today = timezone.now().date()
        
        # Get active batches
        active_batches = ChickBatch.objects.filter(batch_status="active")
        
        today_vaccinations = []
        upcoming_vaccinations = []
        pending_vaccinations = []
        
        for batch in active_batches:
            current_age = (today - batch.batch_date).days
            
            # Define vaccination schedule
            vaccination_days = [
                {'day': 7, 'name': 'First Vaccination'},
                {'day': 14, 'name': 'Second Vaccination'},
                {'day': 21, 'name': 'Third Vaccination'}
            ]
            
            for schedule in vaccination_days:
                vaccination_day = schedule['day']
                vaccination_date = batch.batch_date + timezone.timedelta(days=vaccination_day)
                days_until = (vaccination_date - today).days
                
                vaccination_info = {
                    'batch': batch,
                    'batch_uuid': batch.batch_uuid,
                    'farm_name': batch.farm.name if batch.farm else 'No Farm',
                    'vaccination_name': schedule['name'],
                    'scheduled_day': vaccination_day,
                    'due_date': vaccination_date,
                    'days_until': days_until,
                    'days_past_due': abs(days_until) if days_until < 0 else 0,
                    'current_age': current_age,
                    'chick_count': batch.initial_chick_count
                }
                
                # Check if this vaccination is already recorded
                existing_vaccination = VaccinationSchedule.objects.filter(
                    batch=batch,
                    vaccination_date=vaccination_date
                ).first()
                
                if existing_vaccination:
                    if existing_vaccination.status != 'completed':
                        pending_vaccinations.append({
                            **vaccination_info,
                            'status': existing_vaccination.status,
                            'schedule_id': existing_vaccination.id
                        })
                else:
                    # Not yet scheduled
                    if days_until == 0:
                        today_vaccinations.append(vaccination_info)
                    elif days_until > 0 and days_until <= 7:  # Next 7 days
                        upcoming_vaccinations.append(vaccination_info)

        context = {
            'total_vaccines': Vaccine.objects.count(),
            'total_records': VaccinationSchedule.objects.count(),
            'low_stock_count': Vaccine.objects.filter(current_stock__lte=F('minimum_stock_level')).count(),
            'active_batches': active_batches,
            'active_batches_count': active_batches.count(),
            'today_vaccinations': today_vaccinations,
            'pending_vaccinations': pending_vaccinations,
            'upcoming_vaccinations': upcoming_vaccinations,
            'today_date': today,
            'week_end': today + timezone.timedelta(days=7)
        }
        
        return render(request, 'vaccination_main.html', context)
    except Exception as e:
        print(f"Error in vaccination_main: {str(e)}")
        return render(request, 'vaccination_main.html', {
            'error': f"An error occurred: {str(e)}"
        })

@login_required
def delete_vaccination(request, schedule_id):
    """Delete a vaccination schedule"""
    try:
        # Get the vaccination schedule
        schedule = get_object_or_404(VaccinationSchedule, id=schedule_id)
        
        # Store info for message
        vaccine_name = schedule.vaccine.name
        
        # Delete the schedule
        schedule.delete()
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': f'Successfully deleted vaccination schedule for {vaccine_name}'
        })
        
    except VaccinationSchedule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Vaccination schedule not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def edit_vaccination(request, schedule_id):
    # Get the vaccination schedule
    schedule = get_object_or_404(VaccinationSchedule, id=schedule_id)
    
    if request.method == 'POST':
        try:
            # Update the schedule with new data
            schedule.vaccination_date = request.POST.get('vaccination_date')
            schedule.notes = request.POST.get('notes')
            
            # Update status if provided
            new_status = request.POST.get('status')
            if new_status:
                schedule.status = new_status
                
            # Save the changes
            schedule.save()
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Vaccination schedule updated successfully'
                })
            
            # Redirect with success message for regular requests
            messages.success(request, 'Vaccination schedule updated successfully')
            return redirect('vaccination_list')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
            
            messages.error(request, f'Error updating vaccination schedule: {str(e)}')
            return redirect('vaccination_list')
    
    # For GET requests, return the schedule details
    context = {
        'schedule': schedule,
        'vaccines': Vaccine.objects.all(),
        'statuses': VaccinationSchedule.STATUS_CHOICES
    }
    return render(request, 'stakeholder/edit_vaccination.html', context)

@login_required
def vaccination_list(request):
    vaccinations = VaccinationSchedule.objects.all().order_by('-vaccination_date')
    return render(request, 'stakeholder/vaccination_list.html', {
        'vaccinations': vaccinations
    })

@login_required
def stakeholder_vaccination_list(request):
    """View for stakeholders to see vaccinations for their farms"""
    # Get farms owned by the stakeholder
    stakeholder_farms = Farm.objects.filter(owner=request.user)
    
    # Get vaccinations for all batches in their farms
    vaccinations = VaccinationSchedule.objects.filter(
        batch__farm__in=stakeholder_farms
    )
    
    # Ensure all vaccinations have QR codes
    for vaccination in vaccinations:
        if not vaccination.qr_code:
            vaccination.generate_qr_code()
    
    # Order upcoming vaccinations by date (latest first)
    upcoming_vaccinations = vaccinations.filter(
        status='assigned'
    ).order_by('-vaccination_date')
    
    # Order completed vaccinations by date (latest first)
    completed_vaccinations = vaccinations.exclude(
        status='assigned'
    ).order_by('-vaccination_date')
    
    context = {
        'upcoming_vaccinations': upcoming_vaccinations,
        'completed_vaccinations': completed_vaccinations,
        'farms': stakeholder_farms,
    }
    
    return render(request, 'stakeholder/stakeholder_vaccination_list.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from .models import VaccinationSchedule

@login_required
def scan_qr_code(request, pk):
    """Handle QR code scanning for vaccination verification"""
    try:
        vaccination = get_object_or_404(
            VaccinationSchedule, 
            pk=pk,
            batch__farm__owner=request.user,
            status='assigned'
        )
        
        if request.method == 'POST':
            # Assuming you have a way to get the scanned QR code data
            scanned_data = request.POST.get('scanned_data')  # This should be the JSON string from the QR code
            
            # Decode the scanned data
            try:
                qr_data = json.loads(scanned_data)
                
                # Validate the data
                if qr_data.get('vaccination_id') != str(vaccination.pk):
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid QR code for this vaccination.'
                    }, status=400)
                
                # Update vaccination status
                vaccination.status = 'qr_scanned'
                vaccination.save()
                
                # Create audit log
                VaccinationAuditLog.objects.create(
                    vaccination=vaccination,
                    action="QR Code Scanned",
                    performed_by=request.user,
                    notes=f"QR scanned with data: {scanned_data}"
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'QR code scanned successfully.'
                })
                
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid QR code format.'
                }, status=400)
        
        # Render the scanning page
        context = {
            'vaccination': vaccination,
            'page_title': 'Scan QR Code',
            'qr_code_url': vaccination.qr_code.url if vaccination.qr_code else None
        }
        return render(request, 'stakeholder/scan_qr.html', context)
        
    except VaccinationSchedule.DoesNotExist:
        messages.error(request, 'Invalid QR code or vaccination not found')
        return redirect('stakeholder_vaccination_list')
    except Exception as e:
        messages.error(request, f'Error scanning QR code: {str(e)}')
        return redirect('stakeholder_vaccination_list')

@login_required
def stakeholder_scan_qr(request, vaccination_id):
    """Handle QR code scanning for vaccination verification"""
    try:
        # Get the vaccination schedule and verify ownership
        vaccination = get_object_or_404(
            VaccinationSchedule, 
            id=vaccination_id,
            batch__farm__owner=request.user,
            status='assigned'  # Only allow scanning of assigned vaccinations
        )
        
        if request.method == 'POST':
            try:
                # Get location data from request
                data = request.POST
                latitude = data.get('latitude')
                longitude = data.get('longitude')
                
                if not all([latitude, longitude]):
                    return JsonResponse({
                        'success': False,
                        'message': 'Location data is required'
                    }, status=400)
                
                # Update vaccination status and location
                vaccination.scan_coordinates = f"{latitude},{longitude}"
                vaccination.status = 'qr_scanned'
                vaccination.save()
                
                # Create audit log
                VaccinationAuditLog.objects.create(
                    vaccination=vaccination,
                    action="QR Code Scanned",
                    performed_by=request.user,
                    notes=f"QR scanned at coordinates: {vaccination.scan_coordinates}"
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'QR code scanned successfully',
                    'redirect_url': reverse('upload_vaccination_evidence', kwargs={'pk': vaccination.id})
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
        
        # For GET requests, render the scanning page
        context = {
            'vaccination': vaccination,
            'page_title': 'Scan QR Code',
            'qr_code_url': vaccination.qr_code.url if vaccination.qr_code else None
        }
        return render(request, 'stakeholder/scan_qr.html', context)
        
    except VaccinationSchedule.DoesNotExist:
        messages.error(request, 'Invalid QR code or vaccination not found')
        return redirect('stakeholder_vaccination_list')
    except Exception as e:
        messages.error(request, f'Error scanning QR code: {str(e)}')
        return redirect('stakeholder_vaccination_list')

@login_required
def upload_vaccination_evidence(request, pk):
    vaccination = get_object_or_404(
        VaccinationSchedule, 
        pk=pk,
        batch__farm__owner=request.user,
        status='qr_scanned'  # Only allow evidence upload after QR scan
    )
    
    if request.method == 'POST':
        try:
            # Handle file uploads
            vial_photo = request.FILES.get('vial_photo')
            flock_photo = request.FILES.get('flock_photo')
            administration_photo = request.FILES.get('administration_photo')
            
            if vial_photo:
                vaccination.vaccine_vial_photo = vial_photo
            if flock_photo:
                vaccination.flock_photo = flock_photo
            if administration_photo:
                vaccination.administration_photo = administration_photo
                
            # Update status
            vaccination.status = 'evidence_uploaded'
            vaccination.save()
            
            # Create audit log
            VaccinationAuditLog.objects.create(
                vaccination=vaccination,
                action="Evidence Uploaded",
                performed_by=request.user,
                notes="Uploaded vaccination evidence photos"
            )
            
            messages.success(request, 'Evidence uploaded successfully!')
            return redirect('stakeholder_vaccination_list')
            
        except Exception as e:
            messages.error(request, f'Error uploading evidence: {str(e)}')
            
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import VaccinationSchedule   
    
@login_required
@require_http_methods(["POST"])
def validate_vaccine_vial(request, schedule_id):
    """Validate vaccine vial photo and batch number"""
    try:
        schedule = get_object_or_404(
            VaccinationSchedule, 
            id=schedule_id,
            batch__farm__owner=request.user
        )
        
        # Check if photo was uploaded
        if 'vial_photo' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No vial photo provided'
            }, status=400)
            
        # Get batch number
        batch_no = request.POST.get('batch_no')
        if not batch_no:
            return JsonResponse({
                'success': False,
                'error': 'Batch number is required'
            }, status=400)
            
        try:
            # Validate and save the vial photo
            result = schedule.validate_and_save_vial(
                request.FILES['vial_photo'],
                batch_no
            )
            
            return JsonResponse(result)
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
            
    except VaccinationSchedule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Vaccination schedule not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)

@login_required
def update_feed_stock_view(request, feed_id):
    """View for updating feed stock"""
    feed_stock = get_object_or_404(FeedStock, id=feed_id)
    
    if request.method == 'POST':
        try:
            # Add new sacks to existing count
            additional_sacks = int(request.POST.get('number_of_sacks', 0))
            feed_stock.number_of_sacks += additional_sacks
            
            # Update price only if provided and not empty
            new_price = request.POST.get('price_per_sack')
            if new_price and new_price.strip():  # Check if price is provided and not empty
                feed_stock.price_per_sack = Decimal(new_price)
                
            feed_stock.save()
            
            messages.success(request, f'Added {additional_sacks} sacks to {feed_stock.get_feed_type_display()}')
            return redirect('feed_manage')
            
        except Exception as e:
            messages.error(request, f'Error updating feed stock: {str(e)}')
            return redirect('feed_manage')
            
    context = {
        'feed_stock': feed_stock,
        'feed_types': FeedStock.FEED_TYPE_CHOICES,
        'title': 'Update Feed Stock'
    }
    return render(request, 'stakeholder/update_feed_stock.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChickBatch, GrowthPrediction,DailyData
from .prediction_system import ChickGrowthPredictor
from datetime import datetime

@login_required
def growth_prediction_dashboard(request):
    """View for the growth prediction dashboard"""
    active_batches = ChickBatch.objects.filter(
        user=request.user,
        batch_status='active'
    ).order_by('-batch_date')
    
    context = {
        'active_batches': active_batches,
        'page_title': 'Growth Prediction Dashboard'
    }
    return render(request, 'growth_prediction_dashboard.html', context)

@csrf_exempt
@login_required
def predict_weight(request):
    if request.method == 'POST':
        try:
            # Get data from request
            batch_id = request.POST.get('batch_id')
            prediction_data = {
                'day_number': request.POST.get('day_number'),
                'feed_taken': request.POST.get('feed_taken'),
                'water_taken': request.POST.get('water_taken'),
                'temperature': request.POST.get('temperature'),
                'alive_count': request.POST.get('alive_count'),
                'actual_weight': request.POST.get('actual_weight', '')
            }
            
            # Validate batch exists and belongs to user
            batch = ChickBatch.objects.get(id=batch_id, user=request.user)
            
            # Check if prediction for this day already exists
            existing_prediction = GrowthPrediction.objects.filter(
                batch=batch,
                day_number=prediction_data['day_number']
            ).first()
            
            # Initialize predictor
            predictor = ChickGrowthPredictor()
            
            # Make prediction
            prediction_result = predictor.predict(prediction_data)
            
            if existing_prediction:
                # Update existing prediction
                existing_prediction.feed_consumed = prediction_data['feed_taken']
                existing_prediction.water_consumed = prediction_data['water_taken']
                existing_prediction.temperature = prediction_data['temperature']
                existing_prediction.alive_count = prediction_data['alive_count']
                existing_prediction.predicted_weight = prediction_result['predicted_weight']
                existing_prediction.actual_weight = prediction_data['actual_weight'] if prediction_data['actual_weight'] else None
                existing_prediction.weight_difference = prediction_result['weight_difference']
                existing_prediction.growth_status = prediction_result['growth_status']
                existing_prediction.save()
            else:
                # Save new prediction to database
                GrowthPrediction.objects.create(
                    batch=batch,
                    day_number=prediction_data['day_number'],
                    feed_consumed=prediction_data['feed_taken'],
                    water_consumed=prediction_data['water_taken'],
                    temperature=prediction_data['temperature'],
                    alive_count=prediction_data['alive_count'],
                    predicted_weight=prediction_result['predicted_weight'],
                    actual_weight=prediction_data['actual_weight'] if prediction_data['actual_weight'] else None,
                    weight_difference=prediction_result['weight_difference'],
                    growth_status=prediction_result['growth_status']
                )
            
            # Get historical data for chart
            predictions = GrowthPrediction.objects.filter(batch=batch).order_by('day_number')
            history_days = [pred.day_number for pred in predictions]
            predicted_weights = [pred.predicted_weight for pred in predictions]
            actual_weights = [pred.actual_weight if pred.actual_weight else None for pred in predictions]
            
            return JsonResponse({
                'success': True,
                'predicted_weight': prediction_result['predicted_weight'],
                'weight_difference': prediction_result['weight_difference'],
                'growth_status': prediction_result['growth_status'],
                'history_days': history_days,
                'predicted_weights': predicted_weights,
                'actual_weights': actual_weights
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def prediction_history(request, batch_id):
    try:
        batch = get_object_or_404(ChickBatch, id=batch_id, user=request.user)
        predictions = GrowthPrediction.objects.filter(batch=batch).order_by('day_number')
        
        history = []
        for pred in predictions:
            history.append({
                'date': pred.date.strftime('%Y-%m-%d'),
                'day_number': pred.day_number,
                'predicted_weight': float(pred.predicted_weight),
                'actual_weight': float(pred.actual_weight) if pred.actual_weight else None,
                'weight_difference': float(pred.weight_difference) if pred.weight_difference else None,
                'growth_status': pred.growth_status
            })
        
        return JsonResponse({
            'success': True,
            'history': history
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
        
@login_required
def day_prediction(request, batch_id, day_number):
    """API endpoint for fetching prediction data for a specific day"""
    try:
        batch = get_object_or_404(ChickBatch, id=batch_id, user=request.user)
        
        # Try to find prediction for this day
        prediction = GrowthPrediction.objects.filter(
            batch=batch,
            day_number=day_number
        ).first()
        
        if not prediction:
            return JsonResponse({
                'success': True,
                'prediction': None
            })
        
        # Return prediction data
        prediction_data = {
            'date': prediction.date.strftime('%Y-%m-%d'),
            'day_number': prediction.day_number,
            'predicted_weight': prediction.predicted_weight,
            'actual_weight': prediction.actual_weight,
            'weight_difference': prediction.weight_difference,
            'growth_status': prediction.growth_status,
            'feed_consumed': prediction.feed_consumed,
            'water_consumed': prediction.water_consumed,
            'temperature': prediction.temperature,
            'alive_count': prediction.alive_count
        }
        
        return JsonResponse({
            'success': True,
            'prediction': prediction_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def calculate_recommended_sacks(batch, week):
    """Calculate recommended feed sacks for a specific week based on chick count"""
    daily_feed_grams = {
        1: 15, 2: 35, 3: 59,
        4: 88, 5: 102, 6: 121
    }
    
    # Get daily feed requirement for the week
    daily_grams = daily_feed_grams.get(week, 0)
    # Calculate weekly feed in kg ((daily grams * chicks * 7 days) / 1000 for kg)
    weekly_kg = (daily_grams * batch.initial_chick_count * 7) / 1000
    # Convert to sacks (50kg per sack) and round up
    return max(1, round(weekly_kg / 50))


@login_required
def record_feed_consumption(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            batch = get_object_or_404(ChickBatch, id=data['batch_id'])
            
            # Get current feed assignment
            current_assignment = FeedAssignment.objects.filter(
                batch=batch,
                status='acknowledged'
            ).order_by('-week_number').first()
            
            if not current_assignment:
                return JsonResponse({
                    'success': False,
                    'error': 'No active feed assignment found'
                })
            
            # Calculate total consumption
            morning_consumption = Decimal(str(data['morning_consumption']))
            evening_consumption = Decimal(str(data['evening_consumption']))
            total_consumption = morning_consumption + evening_consumption
            
            # Check if enough feed is available from assignment
            if total_consumption > current_assignment.remaining_sacks:
                return JsonResponse({
                    'success': False,
                    'error': f'Not enough feed available. Only {current_assignment.remaining_sacks} sacks remaining'
                })
            
            try:
                # Create consumption record
                consumption = DailyFeedConsumption.objects.create(
                    batch=batch,
                    feed_assignment=current_assignment,
                    date=timezone.now().date(),
                    morning_consumption=morning_consumption,
                    evening_consumption=evening_consumption,
                    notes=data.get('notes', ''),
                    recorded_by=request.user
                )
                
                # Update assignment's consumed amount
                current_assignment.update_consumption(total_consumption)
                
                return JsonResponse({
                    'success': True,
                    'remaining_sacks': float(current_assignment.remaining_sacks),
                    'total_sacks': float(current_assignment.sacks_assigned),
                    'consumption_data': {
                        'date': consumption.date.strftime('%Y-%m-%d'),
                        'morning': float(consumption.morning_consumption),
                        'evening': float(consumption.evening_consumption),
                        'total': float(total_consumption),
                        'remaining': float(current_assignment.remaining_sacks)
                    }
                })
                
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def feed_consumption_history(request, batch_id):
    try:
        batch = get_object_or_404(ChickBatch, id=batch_id)
        current_assignment = FeedAssignment.objects.filter(
            batch=batch,
            status='acknowledged'
        ).order_by('-week_number').first()
        
        history = DailyFeedConsumption.objects.filter(
            batch=batch,
            feed_assignment=current_assignment
        ).order_by('-date')[:7]  # Get last 7 days
        
        history_data = [{
            'date': record.date.strftime('%Y-%m-%d'),
            'morning_consumption': float(record.morning_consumption),
            'evening_consumption': float(record.evening_consumption),
            'total_consumption': float(record.morning_consumption + record.evening_consumption),
            'remaining_sacks': float(record.feed_assignment.remaining_sacks)
        } for record in history]
        
        current_status = {
            'feed_type': current_assignment.feed_type if current_assignment else None,
            'assigned_sacks': float(current_assignment.sacks_assigned) if current_assignment else 0,
            'remaining_sacks': float(current_assignment.remaining_sacks) if current_assignment else 0,
            'week_number': current_assignment.week_number if current_assignment else None
        }
        
        return JsonResponse({
            'success': True,
            'history': history_data,
            'current_status': current_status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def day_feed_consumption(request, batch_id, day_number):
    try:
        batch = get_object_or_404(ChickBatch, id=batch_id)
        target_date = batch.batch_date + timedelta(days=day_number - 1)
        
        # Get feed consumption for the specific day
        consumption = DailyFeedConsumption.objects.filter(
            batch=batch,
            date=target_date
        ).first()
        
        # Get current feed assignment
        current_assignment = FeedAssignment.objects.filter(
            batch=batch,
            status='acknowledged'
        ).order_by('-week_number').first()
        
        consumption_data = None
        if consumption:
            consumption_data = {
                'morning': float(consumption.morning_consumption),
                'evening': float(consumption.evening_consumption),
                'notes': consumption.notes,
                'total': float(consumption.morning_consumption + consumption.evening_consumption)
            }
        
        return JsonResponse({
            'success': True,
            'consumption': consumption_data,
            'feed_type': current_assignment.feed_type if current_assignment else None,
            'remaining_sacks': float(current_assignment.remaining_sacks) if current_assignment else 0,
            'day_number': day_number
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def batch_feed_info(request, batch_id):
    try:
        batch = get_object_or_404(ChickBatch, id=batch_id)
        current_assignment = FeedAssignment.objects.filter(
            batch=batch,
            status='acknowledged'
        ).order_by('-week_number').first()
        
        # Calculate current day
        current_day = (timezone.now().date() - batch.batch_date).days + 1
        
        # Get today's consumption
        today_consumption = DailyFeedConsumption.objects.filter(
            batch=batch,
            date=timezone.now().date()
        ).first()
        
        # Get consumption history
        history = DailyFeedConsumption.objects.filter(
            batch=batch
        ).order_by('-date')[:7]  # Last 7 days
        
        return JsonResponse({
            'success': True,
            'current_feed_type': current_assignment.feed_type if current_assignment else None,
            'total_sacks': float(current_assignment.sacks_assigned) if current_assignment else 0,
            'total_consumed': float(current_assignment.total_consumed) if current_assignment else 0,
            'remaining_sacks': float(current_assignment.remaining_sacks) if current_assignment else 0,
            'current_day': current_day,
            'today_consumption': {
                'morning': float(today_consumption.morning_consumption),
                'evening': float(today_consumption.evening_consumption),
                'notes': today_consumption.notes
            } if today_consumption else None,
            'consumption_history': [{
                'date': record.date.strftime('%Y-%m-%d'),
                'day_number': (record.date - batch.batch_date).days + 1,
                'morning_consumption': float(record.morning_consumption),
                'evening_consumption': float(record.evening_consumption),
                'total_consumption': float(record.total_consumption),
                'remaining_sacks': float(record.feed_assignment.remaining_sacks)
            } for record in history]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
        
        
        
        
        
@login_required
def get_feed_assignments(request, batch_id):
    try:
        batch = get_object_or_404(ChickBatch, id=batch_id)
        assignments = FeedAssignment.objects.filter(batch=batch).order_by('week_number')
        
        assignments_data = [{
            'week_number': assignment.week_number,
            'feed_type': assignment.feed_type,
            'sacks_assigned': float(assignment.sacks_assigned),
            'total_consumed': float(assignment.total_consumed),
            'remaining_sacks': float(assignment.sacks_assigned - assignment.total_consumed),
            'status': assignment.status
        } for assignment in assignments]
        
        return JsonResponse({
            'success': True,
            'assignments': assignments_data,
            'total_feed_sacks': float(batch.total_feed_sacks)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
        
        
# Step 1: Complete Batch View
@login_required
def complete_batch(request, batch_id):
    batch = get_object_or_404(ChickBatch, id=batch_id)
    if request.method == 'POST':
        batch.batch_status = 'completed'
        if batch.calculate_final_metrics():
            messages.success(request, f"Batch completed. FCR: {batch.actual_fcr:.2f}")
            return redirect('batch_details', batch_id=batch_id)
        messages.error(request, "Error calculating final metrics")
    return redirect('batch_list')

# Step 2: Stakeholder Dashboard
@login_required
def stakeholder_dashboard(request):
    completed_batches = ChickBatch.objects.filter(
        farm__owner=request.user,
        batch_status='completed'
    ).order_by('-batch_date')

    context = {
        'batches': completed_batches,
        'total_pending': sum(
            b.stakeholder_payment 
            for b in completed_batches 
            if b.payment_status == 'pending'
        )
    }
    return render(request, 'stakeholder/dashboard.html', context)

# Step 3: Admin Payment Management
@login_required
def admin_payment_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    completed_batches = ChickBatch.objects.filter(
        batch_status='completed'
    ).select_related('farm__owner')

    context = {
        'batches': completed_batches,
        'total_pending_payments': sum(
            b.stakeholder_payment 
            for b in completed_batches 
            if b.payment_status == 'pending'
        )
    }
    return render(request, 'stakeholder/admin_payments.html', context)

# Step 4: Mark Payment Complete
from django.views.decorators.http import require_POST  # Add this import

# Step 1: Complete Batch View
@login_required
def complete_batch(request, batch_id):
    batch = get_object_or_404(ChickBatch, id=batch_id)
    if request.method == 'POST':
        batch.batch_status = 'completed'
        if batch.calculate_final_metrics():
            messages.success(request, f"Batch completed. FCR: {batch.actual_fcr:.2f}")
            return redirect('batch_details', batch_id=batch_id)
        messages.error(request, "Error calculating final metrics")
    return redirect('batch_list')

# Step 2: Stakeholder Dashboard
@login_required
def stakeholder_dashboard(request):
    completed_batches = ChickBatch.objects.filter(
        farm__owner=request.user,
        batch_status='completed'
    ).order_by('-batch_date')

    context = {
        'batches': completed_batches,
        'total_pending': sum(
            b.stakeholder_payment 
            for b in completed_batches 
            if b.payment_status == 'pending'
        )
    }
    return render(request, 'fcr_dashboard.html', context)

# Step 3: Admin Payment Management
@login_required
def admin_payment_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    completed_batches = ChickBatch.objects.filter(
        batch_status='completed'
    ).select_related('farm__owner')

    context = {
        'batches': completed_batches,
        'total_pending_payments': sum(
            b.stakeholder_payment 
            for b in completed_batches 
            if b.payment_status == 'pending'
        )
    }
    return render(request, 'stakeholder/admin_payments.html', context)

# Step 4: Mark Payment Complete
@login_required
@require_POST


def mark_payment_complete(request, batch_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    batch = get_object_or_404(ChickBatch, id=batch_id)
    batch.payment_status = 'paid'
    batch.save()
    
    return JsonResponse({'success': True})

@login_required
@login_required
def recalculate_batch_metrics(request, batch_id):
    batch = get_object_or_404(ChickBatch, id=batch_id)
    
    if batch.batch_status == 'completed':
        success = batch.calculate_final_metrics()
        if success:
            messages.success(request, f"Metrics recalculated for Batch #{batch_id}")
        else:
            messages.error(request, f"Error recalculating metrics for Batch #{batch_id}")
    else:
        messages.warning(request, f"Batch #{batch_id} is not marked as completed")
    
    return redirect('fcr_dashboard')  # Changed from 'stakeholder_dashboard' to 'fcr_dashboard'@login_required
def recalculate_batch_metrics(request, batch_id):
    batch = get_object_or_404(ChickBatch, id=batch_id)
    
    print(f"Recalculating metrics for batch #{batch_id}")
    print(f"Batch status: {batch.batch_status}")
    
    if batch.batch_status == 'completed':
        success = batch.calculate_final_metrics()
        if success:
            messages.success(request, f"Metrics recalculated for Batch #{batch_id}")
            print(f"Recalculation successful. FCR: {batch.actual_fcr}, Payment: {batch.stakeholder_payment}")
        else:
            messages.error(request, f"Error recalculating metrics for Batch #{batch_id}")
            print("Recalculation failed")
    else:
        messages.warning(request, f"Batch #{batch_id} is not marked as completed. Current status: {batch.batch_status}")
        print(f"Batch not completed, status: {batch.batch_status}")
    
    return redirect('fcr_dashboard')

import razorpay
# Initialize Razorpay client once
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
User = get_user_model()

@login_required
def stakeholder_payments_view(request):
    """View to display completed batches with payment information"""
    
    print(f"Request path: {request.path}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"Request path: {request.path}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user.username}")
    print(f"GET params: {request.GET}")
    
    # Rest of your function...
    
    # Before returning the response:
    print("About to render template")
    # Debug code to inspect User model fields
    user_fields = User._meta.get_fields()
    field_names = [field.name for field in user_fields]
    print("User model fields:", field_names)

    # Check if user_type is a relation
    user_type_field = User._meta.get_field('user_type')
    print("user_type field type:", type(user_type_field))
    if isinstance(user_type_field, models.ForeignKey):
    # If it's a foreign key, print the related model
        related_model = user_type_field.related_model
        print("Related model:", related_model)
        # Print the fields of the related model
        related_fields = related_model._meta.get_fields()
        related_field_names = [field.name for field in related_fields]
        print("Related model fields:", related_field_names)
    # Get filter parameters
    stakeholder_id = request.GET.get('stakeholder', '')
    payment_status = request.GET.get('payment_status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    farm_id = request.GET.get('farm', '')
    
    # Build query
    batches = ChickBatch.objects.select_related(
            'farm',
            'farm__owner'
        ).prefetch_related(
            'payments'
        ).filter(
            batch_status='completed'
        )
    
    if stakeholder_id:
        batches = batches.filter(user_id=stakeholder_id)
    
    if payment_status:
        batches = batches.filter(payment_status=payment_status)
    
    if start_date:
        batches = batches.filter(completion_date__gte=start_date)
    
    if end_date:
        batches = batches.filter(completion_date__lte=end_date)
        
    if farm_id:
        batches = batches.filter(farm_id=farm_id)
    
    # Pagination
    paginator = Paginator(batches, 10)  # Show 10 batches per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all stakeholders - let's get users who own farms
    # This is a more reliable approach since we know these users are stakeholders
    stakeholders = User.objects.filter(
        farms__isnull=False  # Users who own at least one farm
    ).distinct()
    
    # Get all farms for the filter dropdown
    farms = Farm.objects.all()
    
    # Create a mapping of stakeholders to their farms for JavaScript
    stakeholder_farms = {}
    for stakeholder in stakeholders:
        stakeholder_farms[stakeholder.id] = list(Farm.objects.filter(owner=stakeholder).values('id', 'name'))
    
    context = {
        'batches': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'stakeholders':User.objects.filter(user_type__name='Stakeholder'),
        'farms': farms,
        'stakeholder_farms': json.dumps(stakeholder_farms),
        'selected_stakeholder': stakeholder_id,
        'selected_payment_status': payment_status,
        'selected_farm': farm_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'stakeholder_payments.html', context)


@login_required
def create_payment(request, batch_id):
    """Create a new payment for a batch"""
    try:
        # Get the batch
        batch = get_object_or_404(ChickBatch, id=batch_id)
        
        # Check if payment already exists
        if batch.payments.exists():
            messages.warning(request, "Payment already exists for this batch.")
            return redirect('process_payment', payment_id=batch.payments.first().id)
        
        # Calculate payment amount (adjust the calculation as per your business logic)
        amount = batch.live_chick_count * 10  # Example: ₹10 per live chick
        
        # Create the payment
        payment = StakeholderPayment.objects.create(
            batch=batch,
            stakeholder=batch.user,
            amount=amount,
            status='pending'
        )
        
        messages.success(request, "Payment created successfully.")
        # Change this line to redirect to process_payment instead of payment_details
        return redirect('process_payment', payment_id=payment.id)
        
    except Exception as e:
        messages.error(request, f"Error creating payment: {str(e)}")
        return redirect('stakeholder_payments')

# Initialize Razorpay client
def payment_details(request, payment_id):
    """View payment details"""
    try:
        payment = StakeholderPayment.objects.select_related(
            'batch', 
            'batch__farm',  # Get farm info
            'stakeholder'   # Get stakeholder info
        ).get(id=payment_id)
        
        context = {
            'payment': payment,
            'batch': payment.batch,
            'farm': payment.batch.farm,
            'stakeholder': payment.stakeholder,
            'can_process': request.user.is_staff and payment.status == 'pending',
            'payment_methods': [method[0] for method in StakeholderPayment.PAYMENT_METHOD_CHOICES]
        }
        
        return render(request, 'payment_details.html', context)
    except Exception as e:
        messages.error(request, f"Error viewing payment details: {str(e)}")
        return redirect('stakeholder_payments')
@login_required
def process_payment(request, payment_id):
    try:
        payment = get_object_or_404(StakeholderPayment, id=payment_id)
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            
            if payment_method == 'cash':
                # Handle cash payment as before
                payment.payment_method = 'cash'
                payment.status = 'completed'
                payment.processed_by = request.user
                payment.save()
                
                if payment.batch:
                    payment.batch.payment_status = 'paid'
                    payment.batch.save()
                
                messages.success(request, "Cash payment recorded successfully!")
                return redirect('payment_details', payment_id=payment_id)
            
            elif payment_method in ['razorpay', 'bank_transfer']:
                try:
                    # Initialize Razorpay client
                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                    
                    # Create Razorpay order
                    amount_in_paise = int(float(payment.amount) * 100)
                    order_data = {
                        'amount': amount_in_paise,
                        'currency': 'INR',
                        'payment_capture': 1,
                        'notes': {
                            'payment_id': payment.id,
                            'batch_id': payment.batch.id if payment.batch else '',
                        }
                    }
                    
                    # Create the order
                    order = client.order.create(data=order_data)
                    print(f"Razorpay order created: {order}")  # Debug print
                    
                    # Update payment record
                    payment.payment_method = payment_method
                    payment.transaction_id = order['id']
                    payment.status = 'processing'
                    payment.save()
                    
                    # Prepare context for template
                    context = {
                        'payment': payment,
                        'razorpay_order_id': order['id'],
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        'amount': amount_in_paise,
                        'currency': 'INR',
                        'stakeholder_name': payment.stakeholder.get_full_name(),
                        'stakeholder_email': getattr(payment.stakeholder, 'email', ''),
                        'stakeholder_phone': getattr(payment.stakeholder, 'phone_number', ''),
                    }
                    
                    return render(request, 'razorpay_checkout.html', context)
                    
                except Exception as e:
                    print(f"Razorpay Error: {str(e)}")  # Debug print
                    messages.error(request, f"Error setting up payment: {str(e)}")
                    return redirect('process_payment', payment_id=payment_id)
        
        # For GET requests
        return render(request, 'process_payment.html', {
            'payment': payment,
            'payment_methods': ['cash', 'razorpay', 'bank_transfer'],
        })
        
    except Exception as e:
        print(f"Process payment error: {str(e)}")
        messages.error(request, f"Error processing payment: {str(e)}")
        return redirect('stakeholder_payments')
    
    
@csrf_exempt  # Required for Razorpay webhook
def razorpay_callback(request):
    """Handle Razorpay payment callback"""
    if request.method == "POST":
        try:
            # Get payment details from POST data
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify the payment signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': signature
            }
            
            try:
                client.utility.verify_payment_signature(params_dict)
                
                # Find the payment record
                payment = StakeholderPayment.objects.get(transaction_id=razorpay_order_id)
                
                # Update payment status
                payment.status = 'completed'
                payment.processed_by = request.user if request.user.is_authenticated else None
                payment.save()
                
                # Update batch payment status
                if payment.batch:
                    payment.batch.payment_status = 'paid'
                    payment.batch.save()
                
                messages.success(request, "Payment completed successfully!")
                return redirect('payment_details', payment_id=payment.id)
                
            except Exception as e:
                # Signature verification failed
                messages.error(request, "Payment verification failed. Please contact support.")
                return redirect('payment_details', payment_id=payment.id)
                
        except Exception as e:
            messages.error(request, f"Error processing payment callback: {str(e)}")
            return redirect('stakeholder_payments')
    
    return redirect('stakeholder_payments')



from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from datetime import datetime

@login_required
def download_bill(request, payment_id):
    try:
        payment = StakeholderPayment.objects.select_related(
            'batch', 'stakeholder', 'batch__farm'
        ).get(id=payment_id)
        
        # Create PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add content to PDF
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, 750, "Payment Receipt")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, 700, f"Receipt No: #{payment.id}")
        p.drawString(50, 680, f"Date: {payment.payment_date.strftime('%B %d, %Y')}")
        p.drawString(50, 660, f"Stakeholder: {payment.stakeholder.full_name}")
        p.drawString(50, 640, f"Farm: {payment.batch.farm.name}")
        
        # Payment details
        p.drawString(50, 600, "Payment Details:")
        p.drawString(70, 580, f"Base Amount: ₹{payment.base_amount}")
        p.drawString(70, 560, f"FCR Bonus: ₹{payment.fcr_bonus}")
        p.drawString(70, 540, f"Mortality Penalty: ₹{payment.mortality_penalty}")
        p.drawString(50, 520, f"Total Amount: ₹{payment.amount}")
        
        # Batch details
        p.drawString(50, 480, "Batch Details:")
        p.drawString(70, 460, f"Batch ID: #{payment.batch.id}")
        p.drawString(70, 440, f"Initial Count: {payment.batch.initial_chick_count}")
        p.drawString(70, 420, f"Final Count: {payment.batch.available_chickens}")
        p.drawString(70, 400, f"Mortality Rate: {payment.batch.mortality_rate:.2f}%")
        p.drawString(70, 380, f"FCR: {payment.batch.actual_fcr:.2f}")
        
        p.showPage()
        p.save()
        
        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="payment_receipt_{payment.id}.pdf"'
        
        return response
        
    except StakeholderPayment.DoesNotExist:
        messages.error(request, "Payment not found.")
        return redirect('stakeholderdash')
    
@login_required
def stakeholderdash(request):
    try:
        print("\n==== DEBUGGING STAKEHOLDER DASHBOARD ====")  # Add this line
        print(f"Request User ID: {request.user.id}")  # Add this line
        
        # Query the database directly
        payments = StakeholderPayment.objects.filter(stakeholder_id=4)  # Explicitly check for user 4
        print(f"Direct DB Query - Payments found: {payments.count()}")  # Add this line
        
        for payment in payments:
            print(f"""
            Found Payment:
            - ID: {payment.id}
            - Amount: {payment.amount}
            - Status: {payment.status}
            - Stakeholder ID: {payment.stakeholder_id}
            """)
        
        # Now get payments for the logged-in user
        user_payments = StakeholderPayment.objects.filter(stakeholder=request.user)
        print(f"User Payments found: {user_payments.count()}")  # Add this line
        
        context = {
            'recent_payments': user_payments,
            'total_payments': user_payments.count(),
            'debug_info': {
                'user_id': request.user.id,
                'payment_count': user_payments.count(),
            },
            # ... rest of your context ...
        }
        
        print("Context prepared with payments:", bool(user_payments))  # Add this line
        
        return render(request, 'stakeholderdash.html', context)
        
    except Exception as e:
        print(f"Error in stakeholderdash: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect('login')

from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from django.shortcuts import get_object_or_404
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from io import BytesIO
from datetime import datetime
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import os
def generate_bill(request, batch_id):
    try:
        # Get the batch and related data
        batch = get_object_or_404(ChickBatch, id=batch_id)
        
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()
        
        # Set up the PDF document with smaller margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#1a237e')
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=10
        )

        # Add header information
        header_data = [
            [Paragraph("Feather Farm Solutions", title_style), 
             Paragraph(f"Bill #{batch.id}", heading_style)],
            [Paragraph("FCR and Payment Statement", subtitle_style),
             Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal'])]
        ]
        
        header_table = Table(header_data, colWidths=[doc.width/2]*2)
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Farm and Batch Details in two columns
        farm_data = [
            ["Farm Name:", batch.farm.name],
            ["Farm Owner:", batch.farm.owner.get_full_name()],  # Changed from stakeholder to farm owner
            ["Contact:", batch.farm.owner.email or "N/A"]  # Changed from stakeholder to farm owner
        ]
        
        batch_data = [
            ["Batch Date:", batch.batch_date.strftime("%B %d, %Y")],
            ["Duration:", f"{batch.duration} days"],
            ["Status:", batch.batch_status.title()]
        ]
        
        details_data = [[
            Table(farm_data, colWidths=[100, 150], 
                  style=[('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]),
            Table(batch_data, colWidths=[100, 150],
                  style=[('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)])
        ]]
        
        details_table = Table(details_data, colWidths=[doc.width/2]*2)
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('PADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 20))
        
        # FCR Metrics in a visually appealing format
        elements.append(Paragraph("Performance Metrics", heading_style))
        
        fcr_color = colors.green if batch.actual_fcr <= 1.7 else \
                    colors.orange if batch.actual_fcr <= 1.9 else colors.red
                    
        mortality_color = colors.green if batch.mortality_rate <= 5 else \
                         colors.orange if batch.mortality_rate <= 8 else colors.red
        
        metrics_data = [[
            Paragraph(f"<font size=14><b>{batch.actual_fcr:.2f}</b></font><br/>FCR",
                     ParagraphStyle('Metric', alignment=1, textColor=fcr_color)),
            Paragraph(f"<font size=14><b>{batch.mortality_rate:.1f}%</b></font><br/>Mortality Rate",
                     ParagraphStyle('Metric', alignment=1, textColor=mortality_color)),
            Paragraph(f"<font size=14><b>{batch.total_feed_sacks}</b></font><br/>Feed Sacks",
                     ParagraphStyle('Metric', alignment=1))
        ]]
        
        metrics_table = Table(metrics_data, colWidths=[doc.width/3]*3)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 20),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
        # Batch Statistics
        elements.append(Paragraph("Batch Statistics", heading_style))
        stats_data = [
            ["Initial Count:", str(batch.initial_chick_count)],
            ["Current Count:", str(batch.live_chick_count)],
            ["Total Feed Used:", f"{batch.total_feed_sacks} sacks"],
            ["Target FCR:", f"{batch.target_fcr:.2f}"],
            ["Actual FCR:", f"{batch.actual_fcr:.2f}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[doc.width/2]*2)
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#666666')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Payment Details with improved styling
        elements.append(Paragraph("Payment Details", heading_style))
        
        # Calculate bonuses and penalties
        fcr_bonus = calculate_fcr_bonus(batch)
        mortality_penalty = calculate_mortality_penalty(batch)
        total_payment = batch.stakeholder_payment + fcr_bonus - mortality_penalty
        
        payment_data = [
            ["Base Payment", f"₹{batch.stakeholder_payment:,.2f}"],
            ["FCR Bonus", f"+₹{fcr_bonus:,.2f}" if fcr_bonus > 0 else "₹0.00"],
            ["Mortality Penalty", f"-₹{mortality_penalty:,.2f}" if mortality_penalty > 0 else "₹0.00"],
            ["Total Payment", f"₹{total_payment:,.2f}"]
        ]
        
        payment_table = Table(payment_data, colWidths=[doc.width/2]*2)
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#1a237e')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TOPPADDING', (-1, -1), (-1, -1), 10),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#dddddd')),
        ]))
        elements.append(payment_table)
        
        # Add footer with terms
        elements.append(Spacer(1, 30))
        terms_style = ParagraphStyle(
            'Terms',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=1
        )
        elements.append(Paragraph("Terms & Conditions:", terms_style))
        elements.append(Paragraph("• FCR Bonus is awarded for FCR below 1.7", terms_style))
        elements.append(Paragraph("• Mortality Penalty applies for mortality rates above 5%", terms_style))
        elements.append(Paragraph("• Payment will be processed within 7 working days", terms_style))
        
        elements.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=1
        )
        elements.append(Paragraph("This is a computer-generated document. No signature required.", footer_style))
        
        # Build the PDF document
        doc.build(elements)
        
        # FileResponse sets the Content-Disposition header
        buffer.seek(0)
        return FileResponse(
            buffer, 
            as_attachment=True, 
            filename=f'FFS_Bill_{batch.id}_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
        
    except Exception as e:
        print(f"Error generating bill: {str(e)}")
        import traceback
        traceback.print_exc()  # This will print the full error traceback
        return HttpResponse(status=500)

def calculate_fcr_bonus(batch):
    # Implement your FCR bonus calculation logic
    if batch.actual_fcr <= 1.7:
        return 1000  # Example bonus
    return 0

def calculate_mortality_penalty(batch):
    # Implement your mortality penalty calculation logic
    if batch.mortality_rate > 5:
        return 500  # Example penalty
    return 0


import csv
from django.http import HttpResponse
import xlsxwriter
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.shortcuts import render

def export_fcr_data(request, format):
    # Get the data
    batches = ChickBatch.objects.all()  # Adjust query as needed
    
    # Prepare the data
    data = [['Batch ID', 'Farm', 'Start Date', 'Duration', 'Status', 'FCR', 'Target FCR', 'Payment Status', 'Payment Amount']]
    for batch in batches:
        data.append([
            batch.id,
            batch.farm.name,
            batch.batch_date.strftime('%Y-%m-%d'),
            f"{batch.duration} days",
            batch.batch_status,
            f"{batch.actual_fcr:.2f}",
            f"{batch.target_fcr:.2f}",
            batch.payment_status,
            f"₹{batch.stakeholder_payment:.2f}"
        ])

    if format == 'csv':
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fcr_data.csv"'
        
        writer = csv.writer(response)
        writer.writerows(data)
        
        return response

    elif format == 'excel':
        # Create Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Add some styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4e73df',
            'color': 'white',
            'border': 1
        })

        # Write the data
        for row_num, row_data in enumerate(data):
            for col_num, cell_data in enumerate(row_data):
                if row_num == 0:
                    worksheet.write(row_num, col_num, cell_data, header_format)
                else:
                    worksheet.write(row_num, col_num, cell_data)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="fcr_data.xlsx"'
        return response

    elif format == 'pdf':
        # Create PDF file
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Create the table
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t)
        doc.build(elements)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="fcr_data.pdf"'
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    return HttpResponse(status=400)

import tensorflow as tf
import numpy as np
from PIL import Image
import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import DiseaseAnalysis, ChickBatch, Farm
from django.db import IntegrityError
from .models import FeedMonitoring, ChickBatch, DiseaseAnalysis, FeedCalculator
# ... other existing imports ...

# Add these imports
import cv2
from skimage import feature
import numpy as np
from PIL import Image
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

class DiseasePredictor:
    def __init__(self):
        try:
            print("\n=== Initializing Models ===")
            model_dir = os.path.join(settings.BASE_DIR, 'models')
            print(f"Model directory: {model_dir}")
            
            # Check CNN model
            cnn_path = os.path.join(model_dir, 'best_cnn_model.h5')
            if not os.path.exists(cnn_path):
                raise Exception(f"CNN model not found at: {cnn_path}")
            print("Loading CNN model...")
            self.cnn_model = tf.keras.models.load_model(cnn_path)
            
            # Check MobileNet model
            mobilenet_path = os.path.join(model_dir, 'mobilenet_model.h5')
            if not os.path.exists(mobilenet_path):
                raise Exception(f"MobileNet model not found at: {mobilenet_path}")
            print("Loading MobileNet model...")
            self.mobilenet_model = tf.keras.models.load_model(mobilenet_path)
            
            # Updated class names order to match model output
            # Changed order: Coccidiosis first, then Healthy
            self.class_names = ['Coccidiosis', 'Healthy', 'New Castle Disease', 'Salmonella']
            print("Models loaded successfully!")
            print(f"Class names order: {self.class_names}")
            
        except Exception as e:
            print(f"ERROR loading models: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def preprocess_image(self, image, target_size, model_type):
        """
        Preprocess the image for model prediction
        """
        try:
            print(f"\nPreprocessing image for {model_type} model, size {target_size}")
            # Convert to RGB if needed
            if image.mode != 'RGB':
                print("Converting image to RGB")
                image = image.convert('RGB')
            
            # Resize image
            print(f"Resizing image from {image.size} to {target_size}")
            image = image.resize(target_size)
            
            # Convert to array and normalize
            img_array = np.array(image)
            print(f"Image array shape: {img_array.shape}")
            
            # Normalize to [0,1]
            img_array = img_array.astype('float32') / 255.0
            print("Normalized image array")
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            print(f"Final array shape: {img_array.shape}")
            
            return img_array
            
        except Exception as e:
            print(f"ERROR in preprocess_image: {str(e)}")
            raise

    def predict(self, image_file):
        try:
            print("\n=== Starting Prediction ===")
            
            # Open and verify image
            print("Opening image...")
            image = Image.open(image_file)
            print(f"Image opened successfully: {image.size} {image.mode}")
            
            # CNN Prediction (128x128)
            print("\nProcessing CNN model...")
            cnn_image = self.preprocess_image(image, (128, 128), 'CNN')
            print("Making CNN prediction...")
            cnn_pred = self.cnn_model.predict(cnn_image, verbose=0)
            print(f"CNN raw predictions: {cnn_pred}")
            
            # MobileNet Prediction (128x128)
            print("\nProcessing MobileNet model...")
            mobilenet_image = self.preprocess_image(image, (128, 128), 'MobileNet')
            print("Making MobileNet prediction...")
            mobilenet_pred = self.mobilenet_model.predict(mobilenet_image, verbose=0)
            print(f"MobileNet raw predictions: {mobilenet_pred}")
            
            # Ensemble predictions
            print("\nCalculating ensemble prediction...")
            ensemble_pred = (cnn_pred + mobilenet_pred) / 2
            predicted_class_idx = np.argmax(ensemble_pred[0])
            confidence = float(ensemble_pred[0][predicted_class_idx] * 100)
            
            print(f"Raw ensemble predictions: {ensemble_pred[0]}")
            print(f"Predicted class index: {predicted_class_idx}")
            print(f"Class mapping: {list(enumerate(self.class_names))}")
            print(f"Predicted disease: {self.class_names[predicted_class_idx]}")
            print(f"Confidence: {confidence}%")
            
            # Calculate all probabilities
            all_probabilities = {
                class_name: float(prob * 100)
                for class_name, prob in zip(self.class_names, ensemble_pred[0])
            }
            print(f"All probabilities: {all_probabilities}")
            
            return {
                'disease': self.class_names[predicted_class_idx],
                'confidence': confidence,
                'all_probabilities': all_probabilities
            }
            
        except Exception as e:
            print(f"ERROR in prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

# Create a single instance of DiseasePredictor
print("\n=== Creating DiseasePredictor Instance ===")
try:
    predictor = DiseasePredictor()
    print("DiseasePredictor initialized successfully")
except Exception as e:
    print(f"Failed to initialize DiseasePredictor: {str(e)}")
    predictor = None



@login_required
def chick_health_recognition(request):
    if request.method == 'POST':
        try:
            print("\n=== Processing Analysis Request ===")
            batch_id = request.POST.get('batch_id')
            image_file = request.FILES.get('image')
            
            if not batch_id or not image_file:
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide both batch and image'
                })
            
            batch = ChickBatch.objects.get(id=batch_id, user=request.user)
            
            # Process image and get predictions
            image = Image.open(image_file)
            processed_image = image.resize((128, 128))
            img_array = np.array(processed_image, dtype=np.uint8)
            model_input = img_array.astype('float32') / 255.0
            model_input = np.expand_dims(model_input, axis=0)
            
            # Get predictions from both models
            print("Getting predictions from both models...")
            cnn_pred = predictor.cnn_model.predict(model_input, verbose=0)
            mobilenet_pred = predictor.mobilenet_model.predict(model_input, verbose=0)
            
            # Weighted ensemble
            ensemble_pred = (0.45 * cnn_pred + 0.55 * mobilenet_pred)
            predicted_class_idx = np.argmax(ensemble_pred[0])
            confidence = float(ensemble_pred[0][predicted_class_idx] * 100)
            predicted_disease = predictor.class_names[predicted_class_idx]
            
            
            # Calculate all probabilities
            all_probabilities = {
                class_name: float(prob * 100)
                for class_name, prob in zip(predictor.class_names, ensemble_pred[0])
            }
            
            print(f"Predicted disease: {predicted_disease} with confidence: {confidence}%")
            
            # Detect symptoms
            symptoms = []
            try:
                # Convert to HSV for color analysis
                cv_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                img_hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
                
                # Check for inflammation (redness)
                red_mask = cv2.inRange(img_hsv, 
                                     np.array([0, 70, 50]), 
                                     np.array([10, 255, 255]))
                red_ratio = np.sum(red_mask) / red_mask.size
                if red_ratio > 0.1:
                    symptoms.append("Inflammation detected")
                    print("Symptom: Inflammation detected")
                
                # Check for lesions (dark spots)
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                dark_spots = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)[1]
                dark_ratio = np.sum(dark_spots == 0) / dark_spots.size
                if dark_ratio > 0.15:
                    symptoms.append("Lesions detected")
                    print("Symptom: Lesions detected")
                
                # Check feather condition
                edges = cv2.Canny(gray, 100, 200)
                edge_density = np.sum(edges) / edges.size
                if edge_density > 0.1:
                    symptoms.append("Abnormal feather pattern")
                    print("Symptom: Abnormal feather pattern")
                
            except Exception as e:
                print(f"Symptom detection error: {str(e)}")
                symptoms.append("Symptom detection unavailable")
            
            # Calculate severity
            severity_score = 0
            if confidence > 90:
                severity_score += 40
            elif confidence > 75:
                severity_score += 30
            elif confidence > 60:
                severity_score += 20
            
            symptom_weight = 60 / 3
            severity_score += len(symptoms) * symptom_weight
            
            if severity_score >= 80:
                severity = "High"
            elif severity_score >= 50:
                severity = "Medium"
            else:
                severity = "Low"
            
            print(f"Severity: {severity} (Score: {severity_score})")
            
            # Get recommendations
            recommendations = {
                'Coccidiosis': {
                    'Low': "Monitor closely. Consider preventive coccidiostat treatment.",
                    'Medium': "Begin immediate treatment with appropriate coccidiostat. Isolate affected birds.",
                    'High': "Urgent veterinary attention needed. Intensive treatment required."
                },
                'New Castle Disease': {
                    'Low': "Increase biosecurity measures. Monitor for respiratory symptoms.",
                    'Medium': "Isolate affected birds. Begin supportive care and contact vet.",
                    'High': "Emergency veterinary intervention required. High risk of spread."
                },
                'Salmonella': {
                    'Low': "Enhance hygiene protocols. Monitor water quality.",
                    'Medium': "Begin antibiotic treatment as prescribed. Isolate affected birds.",
                    'High': "Urgent veterinary care needed. Risk of flock infection high."
                },
                'Healthy': {
                    'Low': "Continue regular health monitoring and maintenance.",
                    'Medium': "Increase monitoring frequency. Check environmental conditions.",
                    'High': "Despite healthy diagnosis, symptoms suggest further investigation."
                }
            }
            
            recommendation = recommendations.get(predicted_disease, {}).get(severity, 
                "Please consult a veterinarian for proper diagnosis and treatment.")
            
            # Create analysis record
            analysis = DiseaseAnalysis.objects.create(
                batch=batch,
                image=image_file,
                predicted_disease=predicted_disease,
                confidence_score=confidence,
                all_probabilities=all_probabilities,
                severity=severity,
                symptoms_detected=symptoms
            )
            
            return JsonResponse({
                'success': True,
                'disease': predicted_disease,
                'confidence': confidence,
                'image_url': analysis.image.url,
                'all_probabilities': all_probabilities,
                'severity': severity,
                'symptoms': symptoms,
                'recommendation': recommendation
            })
            
        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET request handling
    try:
        batches = ChickBatch.objects.filter(user=request.user, batch_status='active')
        analyses = DiseaseAnalysis.objects.filter(batch__user=request.user).order_by('-analyzed_date')
        
        return render(request, 'chick_health_recognition.html', {
            'batches': batches,
            'analyses': analyses
        })
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('stakeholder')
from django.http import JsonResponse
@login_required
def analysis_details_page(request, analysis_id):
    try:
        analysis = DiseaseAnalysis.objects.get(id=analysis_id)
        
        # Define recommendations dictionary
        recommendations = {
            'Coccidiosis': {
                'Low': "Monitor closely. Consider preventive coccidiostat treatment.",
                'Medium': "Begin immediate treatment with appropriate coccidiostat. Isolate affected birds.",
                'High': "Urgent veterinary attention needed. Intensive treatment required."
            },
            'New Castle Disease': {
                'Low': "Increase biosecurity measures. Monitor for respiratory symptoms.",
                'Medium': "Isolate affected birds. Begin supportive care and contact vet.",
                'High': "Emergency veterinary intervention required. High risk of spread."
            },
            'Salmonella': {
                'Low': "Enhance hygiene protocols. Monitor water quality.",
                'Medium': "Begin antibiotic treatment as prescribed. Isolate affected birds.",
                'High': "Urgent veterinary care needed. Risk of flock infection high."
            },
            'Healthy': {
                'Low': "Continue regular health monitoring and maintenance.",
                'Medium': "Increase monitoring frequency. Check environmental conditions.",
                'High': "Despite healthy diagnosis, symptoms suggest further investigation."
            }
        }
        
        # Get recommendation based on disease and severity
        recommendation = recommendations.get(analysis.predicted_disease, {}).get(
            analysis.severity, 
            "Please consult a veterinarian for proper diagnosis and treatment."
        )
        
        # Determine health status
        health_status = "Healthy" if analysis.predicted_disease == "Healthy" else "Unhealthy"
        
        # Use batch ID instead of name
        batch_id = analysis.batch.id if analysis.batch else "Unknown"
        
        context = {
            'analysis': analysis,
            'recommendation': recommendation,
            'health_status': health_status,
            'analyzed_date': analysis.analyzed_date,
            'batch_name': f"Batch #{batch_id}",  # Use ID instead of name
            'all_probabilities': analysis.all_probabilities if hasattr(analysis, 'all_probabilities') else {},
        }
        
        return render(request, 'analysis_details.html', context)
        
    except DiseaseAnalysis.DoesNotExist:
        messages.error(request, "Analysis not found.")
        return redirect('chick_health_recognition')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('chick_health_recognition')



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime

@login_required
def generate_analysis_report(request, analysis_id):
    try:
        analysis = DiseaseAnalysis.objects.get(id=analysis_id)
        
        # Get recommendations dictionary
        recommendations = {
            'Coccidiosis': {
                'Low': "Monitor closely. Consider preventive coccidiostat treatment.",
                'Medium': "Begin immediate treatment with appropriate coccidiostat. Isolate affected birds.",
                'High': "Urgent veterinary attention needed. Intensive treatment required."
            },
            'New Castle Disease': {
                'Low': "Increase biosecurity measures. Monitor for respiratory symptoms.",
                'Medium': "Isolate affected birds. Begin supportive care and contact vet.",
                'High': "Emergency veterinary intervention required. High risk of spread."
            },
            'Salmonella': {
                'Low': "Enhance hygiene protocols. Monitor water quality.",
                'Medium': "Begin antibiotic treatment as prescribed. Isolate affected birds.",
                'High': "Urgent veterinary care needed. Risk of flock infection high."
            },
            'Healthy': {
                'Low': "Continue regular health monitoring and maintenance.",
                'Medium': "Increase monitoring frequency. Check environmental conditions.",
                'High': "Despite healthy diagnosis, symptoms suggest further investigation."
            }
        }
        
        # Get recommendation
        recommendation = recommendations.get(analysis.predicted_disease, {}).get(
            analysis.severity, 
            "Please consult a veterinarian for proper diagnosis and treatment."
        )
        
        # Prepare context
        context = {
            'analysis': analysis,
            'recommendation': recommendation,
            'health_status': "Healthy" if analysis.predicted_disease == "Healthy" else "Unhealthy",
            'analyzed_date': analysis.analyzed_date,
            'batch_name': f"Batch #{analysis.batch.id}",
            'all_probabilities': analysis.all_probabilities,
            'generated_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Render template
        template = get_template('pdf_report.html')
        html = template.render(context)
        
        # Create PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="analysis_report_{analysis_id}.pdf"'
            return response
        
        return HttpResponse("Error generating PDF", status=500)
        
    except DiseaseAnalysis.DoesNotExist:
        return HttpResponse("Analysis not found", status=404)
@login_required
def provide_feedback(request, analysis_id):
    if request.method == 'POST':
        analysis = DiseaseAnalysis.objects.get(id=analysis_id, batch__farm=request.user.farm)
        analysis.correct_label = request.POST.get('correct_label')
        analysis.feedback_provided = True
        analysis.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


from hoteldetails.models import Order
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import send_mail
import traceback
from django.utils.html import strip_tags  # Import strip_tags here
from smtplib import SMTPException  # Import SMTPException here
import logging

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def stakeholder_order_dashboard(request):
    # Debug: Print current user
    print(f"Current user: {request.user}")
    
    # Get all orders for the stakeholder's farm
    all_orders = Order.objects.filter(batch__farm__owner=request.user)
    print(f"Total orders found: {all_orders.count()}")
    
    # Debug: Print all orders details
    for order in all_orders:
        print(f"Order #{order.id}: Status={order.status}, User={order.user}")
    
    orders_by_status = {
        'all': all_orders,
        'pending': all_orders.filter(status='pending'),
        'confirmed': all_orders.filter(status='confirmed'),
        'out_for_delivery': all_orders.filter(status='out_for_delivery'),
        'delivered': all_orders.filter(status='delivered'),
        'rejected': all_orders.filter(status='rejected')
    }
    
    # Debug: Print counts for each status
    for status, queryset in orders_by_status.items():
        print(f"{status} orders count: {queryset.count()}")
        if queryset.exists():
            print(f"Sample {status} order IDs: {list(queryset.values_list('id', flat=True))}")
    
    context = {
        'orders': orders_by_status,
    }
    
    # Debug: Print context data
    print("Context data:")
    for status, orders in orders_by_status.items():
        print(f"{status}: {orders.count()} orders")
    
    return render(request, 'order_dashboard.html', context)

@login_required
@require_POST
def update_delivery_status(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, batch__farm__owner=request.user)
        print(f"\n=== Starting Delivery Process ===")
        print(f"Processing order #{order.id}")
        
        if request.POST.get('action') == 'start_delivery':
            try:
                # Get hotel name
                hotel_user = order.user.hotel_users.first()
                hotel_name = hotel_user.hotel_name if hotel_user else "Valued Customer"
                print(f"Hotel Name: {hotel_name}")
                print(f"Customer Email: {order.user.email}")

                # Update order status first
                order.status = 'out_for_delivery'
                order.save()
                print(f"Order status updated to: {order.status}")

                # Prepare email content
                subject = f'Order #{order.id} Delivery Started'
                context = {
                    'order': order,
                    'hotel_name': hotel_name,
                    'delivery_date': order.delivery_date,
                    'one_kg_count': order.one_kg_count,
                    'two_kg_count': order.two_kg_count,
                    'three_kg_count': order.three_kg_count,
                    'total_price': order.price,
                }
                
                # Sending email
                try:
                    html_message = render_to_string('emails/delivery_started.html', context)
                    plain_message = strip_tags(html_message)
                    
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[order.user.email],
                        html_message=html_message,
                        fail_silently=True  # Prevents exceptions from being raised
                    )
                    print("Delivery notification email sent successfully!")
                    messages.success(request, f'Started delivery for order #{order.id} and notification sent')
                    
                except Exception as email_error:
                    logger.error(f"Email notification failed: {str(email_error)}")
                    messages.warning(request, f'Email notification failed: {str(email_error)}')

            except Exception as e:
                print(f"\n=== Process Error ===")
                print(f"Error Type: {type(e).__name__}")
                print(f"Error Message: {str(e)}")
                traceback.print_exc()
                messages.warning(request, 'Order status updated but email notification failed')

    except Exception as e:
        print(f"\n=== View Error ===")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        traceback.print_exc()
        messages.error(request, 'Error updating order status')

    return redirect('stakeholder_order_dashboard')



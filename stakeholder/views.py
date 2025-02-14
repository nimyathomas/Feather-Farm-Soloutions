from django.db import IntegrityError
from .models import FeedMonitoring, ChickBatch, DiseaseAnalysis, FeedCalculator
from django.shortcuts import render, redirect
from .forms import BatchSelectionForm, ChickenBatchForm, CompletedBatchUpdateForm
from django.shortcuts import render
from .forms import DailyComparisonForm
from .forms import DailyComparisonForm  # Ensure this is the correct import

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
from django.http import HttpResponse, FileResponse
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

# At the top of views.py, add this debug code
MODEL_PATH = os.path.join(settings.BASE_DIR, 'stakeholder', 'models', 'poultry_disease_classifier_retrained.h5')
print(f"\nAttempting to load model from: {MODEL_PATH}")
print(f"File exists: {os.path.exists(MODEL_PATH)}")

try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        # Test model with random data
        test_input = np.random.random((1, 150, 150, 3))
        test_pred = model.predict(test_input)
        print("\nModel test prediction shape:", test_pred.shape)
        print("Model loaded and tested successfully")
    else:
        print("Model file not found!")
        model = None
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model = None

CLASS_MAPPING = {
    0: "Healthy",
    1: "Coccidiosis",
    2: "New Castle Disease",
    3: "Salmonella"
}

def predict_disease(image_file):
    """ML-based disease detection"""
    try:
        # Preprocess image
        img = Image.open(image_file).convert('RGB')
        img = img.resize((150, 150))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Make prediction using model
        if model is not None:
            # Get model predictions with debug info
            prediction = model.predict(img_array)
            print("\nRaw Predictions:", prediction[0])  # Debug print
            
            predicted_class = np.argmax(prediction[0])
            confidence = float(prediction[0][predicted_class]) * 100
            
            # Print debug information
            print(f"\nPredicted Class Index: {predicted_class}")
            print(f"Class Mapping: {CLASS_MAPPING}")
            print(f"Predicted Disease: {CLASS_MAPPING[predicted_class]}")
            print(f"Confidence: {confidence:.2f}%")
            
            # Add probabilities for all classes
            all_probs = {
                CLASS_MAPPING[i]: f"{float(prediction[0][i])*100:.2f}%"
                for i in range(len(CLASS_MAPPING))
            }
            print("\nAll Probabilities:", all_probs)
            
            return {
                "disease": CLASS_MAPPING[predicted_class],
                "confidence": f"{confidence:.2f}%",
                "severity": "High" if confidence > 80 else "Medium" if confidence > 60 else "Low",
                "symptoms": get_disease_symptoms(CLASS_MAPPING[predicted_class].lower()),
                "all_probabilities": all_probs
            }
        else:
            print("Model is None - falling back to rule-based prediction")
            return {
                "disease": "Error",
                "confidence": "0.00%",
                "severity": "Unknown",
                "symptoms": [],
                "error": "Model not loaded properly"
            }
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}

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


@login_required  # Ensure only logged-in users can add daily data
def add_daily_data(request):
    selected_batch = None
    initial_alive_count = 0
    updated_alive_count = 0
    updated_mortality_count = 0

    # Filter batches based on the logged-in user
    all_batches = ChickBatch.objects.filter(user=request.user)

    # Initialize selected_batch_id from the session
    selected_batch_id = request.session.get("selected_batch", None)

    # Check if a batch was submitted and store it in the session
    if request.method == "POST":
        selected_batch_id = request.POST.get("batch")
        # Store the selected batch ID in the session
        request.session["selected_batch"] = selected_batch_id

        # Handle saving daily data
        date_list = request.POST.getlist("date[]")
        sick_chicks_list = request.POST.getlist("sick_chicks[]")
        mortality_count_list = request.POST.getlist("mortality_count[]")
        feed_uplifted_list = request.POST.getlist("feed_uplifted[]")
        water_consumption_list = request.POST.getlist("water_consumption[]")
        weight_gain_list = request.POST.getlist("weight_gain[]")
        temperature_list = request.POST.getlist("temperature[]")

        # Get the selected batch object
        selected_batch = get_object_or_404(ChickBatch, id=selected_batch_id)

        # Initialize the previous day's alive count
        previous_day_data = (
            DailyData.objects.filter(batch=selected_batch).order_by("-date").first()
        )
        initial_alive_count = selected_batch.initial_chick_count

        # Loop through submitted daily entries
        for i in range(len(date_list)):
            date = date_list[i]
            sick_chicks = int(sick_chicks_list[i]) if sick_chicks_list[i] else 0
            mortality_count = (
                int(mortality_count_list[i]) if mortality_count_list[i] else 0
            )
            feed_uplifted = (
                float(feed_uplifted_list[i]) if feed_uplifted_list[i] else 0.0
            )
            water_consumption = (
                float(water_consumption_list[i]) if water_consumption_list[i] else 0.0
            )
            weight_gain = float(weight_gain_list[i]) if weight_gain_list[i] else 0.0
            temperature = float(temperature_list[i]) if temperature_list[i] else 0.0

            # Validation checks
            if (
                sick_chicks < 0
                or feed_uplifted < 0
                or water_consumption < 0
                or weight_gain < 0
                or mortality_count < 0
            ):
                messages.error(request, "Input values cannot be negative.")
                return redirect("add_daily_data")

            # Calculate updated alive count before checking mortality
            updated_alive_count = initial_alive_count - updated_mortality_count

            # Check if mortality count exceeds updated alive count or initial chick count
            if mortality_count > updated_alive_count:
                messages.error(
                    request, "Mortality count cannot exceed the updated alive count."
                )
                return redirect("add_daily_data")
            if mortality_count > initial_alive_count:
                messages.error(
                    request, "Mortality count cannot exceed the initial chick count."
                )
                return redirect("add_daily_data")

            # Check if a record already exists for the same batch and date
            existing_record = DailyData.objects.filter(
                batch=selected_batch, date=date
            ).exists()
            if existing_record:
                messages.error(
                    request, f"Data for { date} already exists for this batch."
                )
                return redirect("add_daily_data")  # Redirect back to the form

            # Calculate alive_count based on previous day's data
            if previous_day_data:
                alive_count = previous_day_data.alive_count - mortality_count
            else:
                alive_count = initial_alive_count - mortality_count

            # Ensure alive_count is not negative
            if alive_count < 0:
                messages.error(request, "Calculated alive count cannot be negative.")
                return redirect("add_daily_data")

            # Create a new daily data record
            DailyData.objects.create(
                batch=selected_batch,
                date=date,
                alive_count=alive_count,
                sick_chicks=sick_chicks,
                mortality_count=mortality_count,
                feed_uplifted=feed_uplifted,
                water_consumption=water_consumption,
                weight_gain=weight_gain,
                temperature=temperature,
                owner=request.user,
            )

            # Update previous_day_data to the newly created one
            previous_day_data = DailyData.objects.filter(
                batch=selected_batch, date=date
            ).first()

        messages.success(request, "Daily data has been saved successfully.")
        return redirect("add_daily_data")  # Replace with your actual view name

    # Get the selected batch from the session if exists
    if selected_batch_id:
        selected_batch = get_object_or_404(ChickBatch, id=selected_batch_id)
        updated_mortality_count = (
            DailyData.objects.filter(batch=selected_batch).aggregate(
                Sum("mortality_count")
            )["mortality_count__sum"]
            or 0
        )
        # Get initial chick count again
        initial_alive_count = selected_batch.initial_chick_count
        updated_alive_count = initial_alive_count - updated_mortality_count

    return render(
        request,
        "daily_batch.html",
        {
            "all_batches": all_batches,
            "selected_batch": selected_batch,
            "initial_chick_count": initial_alive_count,
            "updated_alive_count": updated_alive_count,
            "updated_mortality_count": updated_mortality_count,
        },
    )


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
    paginator = Paginator(daily_data_records, 10)  # Show 10 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
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
        if "post_title" in request.POST:  # Handle new post
            title = request.POST.get("post_title")
            content = request.POST.get("post_content")
            Post.objects.create(title=title, content=content, owner=request.user)
            return redirect(
                "forum_dashboard"
            )  # Redirect to forum page after creating a post

        elif "comment_content" in request.POST:  # Handle new comment
            content = request.POST.get("comment_content")
            Comment.objects.create(
                content=content, post=selected_post, owner=request.user
            )
            return redirect("forum_dashboard", post_id=post_id)  # Stay on the same chat

    context = {
        "posts": posts,
        "selected_post": selected_post,
        "comments": comments,
    }
    return render(request, "forum/forum_dashboard.html", {"posts": posts})




# views.py
from django.shortcuts import render

def chat_room(request, room_name):
    # Pass the room name to the template
    return render(request, 'chat_room.html', {
        'room_name': room_name
    })

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

@login_required
@login_required
def chick_health_recognition(request):
    """View for disease prediction"""
    batches = ChickBatch.objects.filter(batch_status='active').order_by('-batch_date')
    
    if request.method == 'POST' and request.FILES.get('chick_image'):
        try:
            image_file = request.FILES['chick_image']
            batch_id = request.POST.get('batch_id')
            
            # Ensure batch_id is provided
            if not batch_id:
                messages.error(request, 'Please select a batch')
                return redirect('chick_health_recognition')

            # Fetch the batch safely
            selected_batch = ChickBatch.objects.filter(id=batch_id).first()
            if not selected_batch:
                messages.error(request, f'Batch with ID {batch_id} not found.')
                return redirect('chick_health_recognition')

            # Process the image file directly
            result = predict_disease(image_file)
            print(f"🔍 Debug Output from predict_disease: {result}")  # ✅ Debugging step
            
            # Ensure result is a dictionary
            if isinstance(result, dict) and "disease" in result and "confidence" in result:
                predicted_class = result["disease"]
                confidence_score = float(result["confidence"].strip('%'))  # Convert to float
                symptoms_detected = result.get("symptoms", [])  # Get symptoms if available
                severity = result.get("severity", "Unknown")  # Default to "Unknown" if missing
            else:
                raise ValueError(f"Unexpected return value from predict_disease: {result}")

            # Save the analysis
            analysis = DiseaseAnalysis.objects.create(
                image=image_file,
                predicted_disease=predicted_class,
                confidence_score=confidence_score,
                symptoms_detected=symptoms_detected,
                batch=selected_batch,
                created_by=request.user
            )
            
            messages.success(request, 'Analysis completed successfully!')
            return redirect('disease_analysis_detail', analysis_id=analysis.id)
            
        except Exception as e:
            messages.error(request, f'Error processing image: {str(e)}')
            return redirect('chick_health_recognition')
    
    context = {
        'batches': batches,
        'recent_analyses': DiseaseAnalysis.objects.all().order_by('-analyzed_date')[:5]
    }
    
    return render(request, 'chick_health_recognition.html', context)




def get_disease_symptoms(disease):
    """Return common symptoms for each disease"""
    symptoms_map = {
        'healthy': [],
        'coccidiosis': ['Bloody droppings', 'Lethargy', 'Ruffled feathers'],
        'new castle disease': ['Respiratory distress', 'Nervous symptoms', 'Drop in egg production'],
        'salmonella': ['Diarrhea', 'Loss of appetite', 'Depression']
    }
    return symptoms_map.get(disease.lower(), [])

@login_required
def disease_analysis_list(request):
    """View to display list of disease analyses"""
    analyses = DiseaseAnalysis.objects.filter(
        batch__user=request.user
    ).order_by('-analyzed_date')
    
    return render(request, 'stakeholder/disease_analysis_list.html', {
        'analyses': analyses
    })

@login_required
def disease_analysis_detail(request, analysis_id):
    """View to display details of a specific analysis"""
    analysis = get_object_or_404(DiseaseAnalysis, 
                                id=analysis_id, 
                                batch__user=request.user)
    
    return render(request, 'stakeholder/disease_analysis_detail.html', {
        'analysis': analysis
    })

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

@login_required
def provide_feedback(request, analysis_id):
    """Handle feedback for model predictions"""
    analysis = get_object_or_404(DiseaseAnalysis, id=analysis_id, batch__user=request.user)
    
    if request.method == 'POST':
        correct_label = request.POST.get('correct_label')
        
        if correct_label:
            # Update the analysis with feedback
            analysis.predicted_disease = correct_label
            analysis.save()
            
            messages.success(request, "Thank you for your feedback!")
        else:
            messages.error(request, "Please provide a correct label")
            
    return redirect('disease_analysis_detail', analysis_id=analysis_id)

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
    feed_stocks = FeedStock.objects.all()
    form = FeedStockForm()
    context = {
        'feed_stocks': feed_stocks,
        'form': form,
        'is_admin': request.user.is_staff
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
def feed_manage(request):
    """Feed management view"""
    feed_stocks = FeedStock.objects.all()

    if request.method == 'POST':
        # Check if it's an edit or add operation
        if 'edit' in request.POST:
            # Edit existing feed stock
            feed_stock = get_object_or_404(FeedStock, pk=request.POST.get('id'))
            form = FeedStockForm(request.POST, instance=feed_stock)
            if form.is_valid():
                form.save()
                messages.success(request, 'Feed stock updated successfully!')
                return redirect('feed_manage')
            else:
                messages.error(request, 'Error updating feed stock. Please check the form.')
        else:
            # Add new feed stock
            form = FeedStockForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Feed stock added successfully!')
                return redirect('feed_manage')
            else:
                messages.error(request, 'Error adding feed stock. Please check the form.')
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
    # Get feed stocks by exact type names matching the database
    starter_stocks = FeedStock.objects.filter(feed_type='starter')
    grower_stocks = FeedStock.objects.filter(feed_type='grower')
    finisher_stocks = FeedStock.objects.filter(feed_type='finisher')
    
    # Calculate totals for each type
    starter_feed = {
        'total_sacks': sum(s.number_of_sacks for s in starter_stocks),
        'total_value': sum(s.number_of_sacks * s.price_per_sack for s in starter_stocks),
        'is_low': any(s.number_of_sacks <= s.minimum_sacks for s in starter_stocks),
        'stocks': starter_stocks,
        'display_name': 'Starter Feed'
    }
    
    grower_feed = {
        'total_sacks': sum(s.number_of_sacks for s in grower_stocks),
        'total_value': sum(s.number_of_sacks * s.price_per_sack for s in grower_stocks),
        'is_low': any(s.number_of_sacks <= s.minimum_sacks for s in grower_stocks),
        'stocks': grower_stocks,
        'display_name': 'Grower Feed'
    }
    
    finisher_feed = {
        'total_sacks': sum(s.number_of_sacks for s in finisher_stocks),
        'total_value': sum(s.number_of_sacks * s.price_per_sack for s in finisher_stocks),
        'is_low': any(s.number_of_sacks <= s.minimum_sacks for s in finisher_stocks),
        'stocks': finisher_stocks,
        'display_name': 'Finisher Feed'
    }
    
    # Get all stocks for the table
    all_stocks = FeedStock.objects.all()
    
    # Calculate total value for each stock
    for stock in all_stocks:
        stock.total_value = stock.number_of_sacks * stock.price_per_sack
    
    context = {
        'starter_feed': starter_feed,
        'grower_feed': grower_feed,
        'finisher_feed': finisher_feed,
        'feed_stocks': all_stocks,
        'is_admin': request.user.is_staff,
        'form': FeedStockForm() if request.user.is_staff else None,
        'debug': True  # Add this to see debug information
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
def delete_feed(request, feed_id):
    """Delete feed stock"""
    if request.method == 'POST':
        try:
            feed_stock = get_object_or_404(FeedStock, id=feed_id)
            feed_type = feed_stock.feed_type
            feed_stock.delete()
            messages.success(request, f'Successfully deleted {feed_type}')
        except Exception as e:
            messages.error(request, f'Error deleting feed stock: {str(e)}')
            
    return redirect('feed_manage')



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
    """View for listing active batches with their feed status"""
    # Get filter parameters
    farm_search = request.GET.get('farm_search', '')
    feed_type = request.GET.get('feed_type', '')
    week_filter = request.GET.get('week', '')
    
    # Get active batches
    batches = ChickBatch.objects.filter(batch_status='active')
    
    if farm_search:
        batches = batches.filter(farm__farm_name__icontains=farm_search)
    
    batch_feed_data = []
    for batch in batches:
        days_since_start = (timezone.now().date() - batch.batch_date).days
        current_week = min((days_since_start // 7) + 1, 6)
        
        # Determine feed type based on week
        if current_week == 1:
            feed_type = 'Starter Feed'
            week_percentage = 0.15
        elif 2 <= current_week <= 4:
            feed_type = 'Grower Feed'
            week_percentage = 0.20
        else:
            feed_type = 'Finisher Feed'
            week_percentage = 0.125
        
        # Get available feed stocks for this type
        available_feed_stocks = FeedStock.objects.filter(
            feed_type=feed_type,
            number_of_sacks__gt=0
        )
        
        batch_feed_data.append({
            'batch': batch,
            'current_week': current_week,
            'feed_type': feed_type,
            'recommended_sacks': round(week_percentage * batch.initial_chick_count),
            'total_sacks_needed': round(batch.initial_chick_count * 4.2 / 50),
            'sacks_assigned': 0,
            'can_assign': False,
            'available_feed_stocks': available_feed_stocks,
            'assigned_weeks': []
        })
    
    context = {
        'batch_feed_data': batch_feed_data,
        'active_filters': {
            'farm_search': farm_search,
            'feed_type': feed_type,
            'week': week_filter
        }
    }
    
    return render(request, 'stakeholder/active_batch_feed.html', context)

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
            
            # Validate feed stock
            feed_stock = get_object_or_404(FeedStock, id=feed_stock_id)
            
            # Create feed assignment
            FeedAssignment.objects.create(
                batch=batch,
                week_number=week_number,
                sacks_assigned=sacks_assigned,
                cost_per_sack=feed_stock.price_per_sack,
                total_cost=sacks_assigned * feed_stock.price_per_sack
            )
            
            messages.success(request, f'Successfully assigned feed for Week {week_number}')
            
        except Exception as e:
            messages.error(request, f"Error assigning feed: {str(e)}")
    
    return redirect('active_batches_feed')




@login_required
@transaction.atomic
def batch_feed_assignment(request, batch_id):
    """Handle feed assignment for a specific batch"""
    batch = get_object_or_404(ChickBatch, id=batch_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            week_number = int(request.POST.get('week_number'))
            sacks_assigned = int(request.POST.get('sacks_assigned'))
            feed_stock_id = request.POST.get('feed_stock')
            
            # Validate feed stock
            feed_stock = get_object_or_404(FeedStock, id=feed_stock_id)
            
            # Check if week is already assigned
            if FeedAssignment.objects.filter(batch=batch, week_number=week_number).exists():
                raise ValueError(f"Week {week_number} already has a feed assignment")
            
            # Validate sequential assignment
            if week_number > 1:
                prev_week = FeedAssignment.objects.filter(
                    batch=batch, 
                    week_number=week_number-1
                ).exists()
                if not prev_week:
                    raise ValueError(f"Must assign Week {week_number-1} first")
            
            # Check feed stock availability
            if feed_stock.number_of_sacks < sacks_assigned:
                raise ValueError("Not enough feed stock available")
            
            # Create feed assignment
            assignment = FeedAssignment.objects.create(
                batch=batch,
                week_number=week_number,
                sacks_assigned=sacks_assigned,
                cost_per_sack=feed_stock.price_per_sack,
                total_cost=sacks_assigned * feed_stock.price_per_sack
            )
            
            # Update feed stock
            feed_stock.number_of_sacks -= sacks_assigned
            feed_stock.save()
            
            messages.success(
                request, 
                f'Successfully assigned {sacks_assigned} sacks for Week {week_number}'
            )
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f'Successfully assigned {sacks_assigned} sacks of {feed_stock.get_feed_type_display()} for Week {week_number}'
                })
            
        except ValueError as e:
            messages.error(request, str(e))
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        except Exception as e:
            messages.error(request, f"Error assigning feed: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': f"Error assigning feed: {str(e)}"
                })
    
    # For non-AJAX requests, redirect back to the list
    return redirect('active_batches_feed')
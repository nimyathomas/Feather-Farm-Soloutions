from django.db import IntegrityError
from .models import FeedMonitoring
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
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from stakeholder.models import ChickBatch
from user.models import User
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
    return redirect("/")


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
from .models import Farm, ChickBatch
from django.contrib.auth.decorators import login_required

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


# stakeholder/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DiseaseAnalysis, ChickBatch
from .forms import DiseaseAnalysisForm
import tensorflow as tf
import numpy as np
from PIL import Image
import io

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

@login_required
def create_disease_analysis(request, batch_id):
    batch = get_object_or_404(ChickBatch, id=batch_id, user=request.user)
    
    if request.method == 'POST':
        form = DiseaseAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.batch = batch
            analysis.created_by = request.user
            
            # Process the image and get predictions
            try:
                image = request.FILES['image']
                prediction = predict_disease(image)
                
                analysis.predicted_disease = prediction['disease']
                analysis.confidence_score = prediction['confidence']
                analysis.symptoms_detected = prediction['symptoms']
                
                analysis.save()
                messages.success(request, 'Disease analysis created successfully!')
                return redirect('disease_analysis_detail', analysis_id=analysis.id)
                
            except Exception as e:
                messages.error(request, f'Error processing image: {str(e)}')
        else:
            form = DiseaseAnalysisForm()
    
    return render(request, 'stakeholder/create_disease_analysis.html', {
        'form': form,
        'batch': batch
    })

def predict_disease(image_file):
    """
    Process image and predict disease with enhanced coccidiosis detection
    """
    try:
        # 1. Load and preprocess image
        image = Image.open(io.BytesIO(image_file.read())).convert('RGB')
        original_image = np.array(image)
        
        # 2. Analyze image characteristics
        def analyze_image_features(img):
            # Convert to different color spaces
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            
            # Enhanced color analysis for coccidiosis
            red_channel = img[:,:,0]
            red_intensity = np.mean(red_channel) / 255.0
            red_variation = np.std(red_channel) / 255.0
            
            # Analyze brown/reddish colors (typical in coccidiosis)
            brown_mask = (img[:,:,0] > 100) & (img[:,:,1] < 150) & (img[:,:,2] < 150)
            brown_ratio = np.sum(brown_mask) / (img.shape[0] * img.shape[1])
            
            # Return all features in a dictionary
            return {
                'red_intensity': red_intensity,
                'red_variation': red_variation,
                'brown_ratio': brown_ratio,
                'texture': np.std(lab[:,:,0]) / 255.0
            }
        
        # Get image features
        features = analyze_image_features(original_image)
        print("\nImage Features:")
        for key, value in features.items():
            print(f"{key}: {value:.3f}")
        
        # 3. Prepare image for model
        image = image.resize((150, 150))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        # 4. Get model prediction
        model = load_disease_model()
        prediction = model.predict(image_array)
        raw_predictions = prediction[0]
        
        diseases = ['healthy', 'coccidiosis', 'salmonella', 'aspergillosis']
        
        # 5. Apply coccidiosis-specific rules
        coccidiosis_indicators = 0
        
        # Check red/brown coloration using features from the dictionary
        if features['red_intensity'] > 0.4:
            coccidiosis_indicators += 1
        if features['brown_ratio'] > 0.2:
            coccidiosis_indicators += 1
        if features['red_variation'] > 0.15:
            coccidiosis_indicators += 1
        
        # Get initial predictions
        initial_predictions = {
            disease: float(prob)
            for disease, prob in zip(diseases, raw_predictions)
        }
        
        print("\nInitial Predictions:")
        for disease, prob in initial_predictions.items():
            print(f"{disease}: {prob*100:.2f}%")
        
        # 6. Adjust predictions based on visual indicators
        if coccidiosis_indicators >= 2:
            print("\nDetected strong visual indicators of coccidiosis")
            # Boost coccidiosis probability
            initial_predictions['coccidiosis'] *= 2.0
            initial_predictions['healthy'] *= 0.5
        
        # 7. Make final decision
        if initial_predictions['coccidiosis'] > 0.3 or coccidiosis_indicators >= 2:
            predicted_disease = 'coccidiosis'
            confidence = min(initial_predictions['coccidiosis'] * 100 * 1.5, 100)
        else:
            predicted_disease = max(initial_predictions.items(), key=lambda x: x[1])[0]
            confidence = initial_predictions[predicted_disease] * 100
        
        print("\nFinal Decision:")
        print(f"Selected Disease: {predicted_disease}")
        print(f"Confidence: {confidence:.2f}%")
        print(f"Coccidiosis Indicators Found: {coccidiosis_indicators}")
        
        # Get symptoms for the predicted disease
        symptoms = get_disease_symptoms(predicted_disease)
        
        return {
            'disease': predicted_disease,
            'confidence': float(confidence),
            'symptoms': symptoms,
            'all_predictions': {
                disease: float(initial_predictions[disease] * 100)
                for disease in diseases
            },
            'is_diseased': predicted_disease != 'healthy',
            'status': 'Healthy' if predicted_disease == 'healthy' else 'Disease Detected',
            'metrics': {
                'severity': min(confidence, 100),
                'urgency': 100 if predicted_disease != 'healthy' else 0
            }
        }
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        raise ValueError(f"Error in disease prediction: {str(e)}")

def get_disease_symptoms(disease):
    """
    Return common symptoms for each disease
    """
    symptoms_map = {
        'coccidiosis': ['Bloody droppings', 'Lethargy', 'Ruffled feathers'],
        'salmonella': ['Diarrhea', 'Loss of appetite', 'Depression'],
        'aspergillosis': ['Breathing difficulty', 'Gasping', 'Weight loss'],
        'healthy': []
    }
    return symptoms_map.get(disease, [])

def load_disease_model():
    try:
        model_path = os.path.join(settings.BASE_DIR, 'stakeholder', 'models', 'poultry_disease_classifier.h5')
        
        # Add custom metrics if you used any during training
        model = tf.keras.models.load_model(model_path, compile=False)
        
        # Compile with same settings as training
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

@login_required
def chick_health_recognition(request):
    """View for disease prediction page"""
    # Get user's batches
    batches = ChickBatch.objects.filter(user=request.user).order_by('-batch_date')
    
    # Get recent analyses
    recent_analyses = DiseaseAnalysis.objects.filter(
        batch__user=request.user
    ).order_by('-analyzed_date')[:5]
    
    if request.method == 'POST' and request.FILES.get('chick_image'):
        try:
            image_file = request.FILES['chick_image']
            batch_id = request.POST.get('batch_id')
            
            # Validate batch exists and belongs to user
            if not batch_id:
                messages.error(request, "Please select a batch")
                return render(request, 'chick_health_recognition.html', {
                    'batches': batches,
                    'recent_analyses': recent_analyses
                })
                
            batch = get_object_or_404(ChickBatch, id=batch_id, user=request.user)
            
            # Get prediction
            result = predict_disease(image_file)
            
            # Save analysis
            analysis = DiseaseAnalysis.objects.create(
                batch=batch,
                created_by=request.user,
                image=image_file,
                predicted_disease=result['disease'],
                confidence_score=result['confidence'],
                symptoms_detected=result.get('symptoms', []),
                analyzed_date=timezone.now()
            )
            
            messages.success(request, "Analysis completed successfully!")
            return render(request, 'chick_health_recognition.html', {
                'result': result,
                'analysis': analysis,
                'batches': batches,
                'recent_analyses': recent_analyses
            })
            
        except Exception as e:
            messages.error(request, f"Error during analysis: {str(e)}")
    
    return render(request, 'chick_health_recognition.html', {
        'batches': batches,
        'recent_analyses': recent_analyses
    })

@login_required
def provide_feedback(request, analysis_id):
    """Handle feedback for model predictions"""
    analysis = get_object_or_404(DiseaseAnalysis, id=analysis_id, batch__user=request.user)
    
    if request.method == 'POST':
        correct_label = request.POST.get('correct_label')
        
        # Save training data
        TrainingData.objects.create(
            image=analysis.image,
            predicted_label=analysis.predicted_disease,
            correct_label=correct_label,
            confidence=analysis.confidence_score
        )
        
        # If we have enough new training data, retrain the model
        if should_retrain_model():
            retrain_model()
            
        messages.success(request, "Thank you for your feedback!")
        
    return redirect('disease_analysis_detail', analysis_id=analysis_id)

def should_retrain_model():
    """Check if we have enough new training data to retrain"""
    new_data_count = TrainingData.objects.filter(verified=False).count()
    return new_data_count >= 50  # Retrain after 50 new samples

def retrain_model():
    """Retrain the model with new data"""
    try:
        # Load existing model
        model = load_disease_model()
        
        # Get new training data
        new_data = TrainingData.objects.filter(verified=False)
        
        # Prepare training data
        X = []
        y = []
        
        for data in new_data:
            # Preprocess image
            image = Image.open(data.image.path)
            image = image.resize((150, 150))
            image_array = np.array(image) / 255.0
            X.append(image_array)
            
            # One-hot encode label
            label_index = ['healthy', 'coccidiosis', 'salmonella', 'aspergillosis'].index(data.correct_label)
            label = np.zeros(4)
            label[label_index] = 1
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Fine-tune model
        model.fit(
            X, y,
            epochs=5,
            batch_size=32,
            validation_split=0.2
        )
        
        # Save updated model
        model.save(os.path.join(settings.BASE_DIR, 'stakeholder', 'models', 'disease_model_updated.h5'))
        
        # Mark data as verified
        new_data.update(verified=True)
        
        print("Model successfully retrained!")
        
    except Exception as e:
        print(f"Error retraining model: {str(e)}")
from django.db import IntegrityError
from .models import FeedMonitoring
from django.shortcuts import render, redirect
from .forms import BatchSelectionForm, ChickenBatchForm, CompletedBatchUpdateForm
from django.shortcuts import render
from .forms import DailyComparisonForm
from .forms import DailyComparisonForm  # Ensure this is the correct import
from .forms import FeedMonitoringForm
from .models import DailyData  # Ensure you import the DailyData model
from .models import DailyData  # Ensure you import your model
from django.shortcuts import get_object_or_404, redirect
from .forms import DailyDataForm
from .models import DailyData
from .models import ChickBatch, DailyData  # Adjust based on your models
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg
from .forms import DailyDataForm  # Assume you have created a form for DailyData
from .models import ChickBatch, DailyData
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
from django.shortcuts import get_object_or_404


def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'services.html')


def contact(request):
    return render(request, 'contact.html')


def logout_view(request):
    logout(request)
    return redirect('/')


# views.py


@login_required
def stakeholder(request):
    user = request.user  # Assuming the user is logged in
    today = timezone.now().date()

    # Fetch chick batches
    chick_batches = user.chick_batches.all().order_by('-batch_date')
    total_chick_count = sum(
        batch.initial_chick_count for batch in chick_batches)

    # Fetch location from query parameters (not from the User model)
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lon')

    # Set up OpenWeatherMap client
    api_key = '6a0179abe35c7736af4f3f57bd4da77e'
    owm = OWM(api_key)

    # Create a WeatherManager instance
    # This should be correct if you're using the right version
    mgr = owm.weather_manager()

    # Fetch weather data based on coordinates or use fallback
    if latitude and longitude:
        try:
            observation = mgr.weather_at_coords(
                float(latitude), float(longitude))
        except Exception as e:
            observation = mgr.weather_at_place('Erattupetta')  # Fallback
    else:
        observation = mgr.weather_at_place('Erattupetta')  # Fallback

    weather = observation.weather

    weather_data = {
        'temperature': weather.temperature('celsius')['temp'],
        'humidity': weather.humidity,
        'wind_speed': weather.wind()['speed'],
    }

    # Handle alerts (add your logic here)
    alert_vaccine_dates = []  # Example alert lists
    upliftment_alert_dates = []
    feed_dates = []

    for batch in chick_batches:
        batch_date = batch.batch_date

        # Calculate vaccination and upliftment dates
        alert_vaccine_dates.append({
            '7th_day': batch_date + timedelta(days=6),
            '14th_day': batch_date + timedelta(days=13),
            '21st_day': batch_date + timedelta(days=20),
            'batch': batch,
        })

        upliftment_alert_dates.append(batch_date + timedelta(days=39))

        # Feed stage reminders (pre-starter, starter, finisher)
        feed_dates.append({
            'pre_starter': batch_date,
            'starter': batch_date + timedelta(days=9),
            'finisher': batch_date + timedelta(days=23),
            'batch': batch,
        })

    # Populate alerts as per your logic...

    context = {
        'chick_batches': chick_batches,
        'total_chick_count': total_chick_count,
        'today': today,
        'user_data': user,
        'weather_data': weather_data,
        'alert_vaccine_dates': alert_vaccine_dates,
        'upliftment_alert_dates': upliftment_alert_dates,
        'feed_dates': feed_dates,

    }

    return render(request, 'stakeholderdash.html', context)


def calculate_feeders_and_drinkers(initial_chick_count):
    feeders = initial_chick_count // 50  # 1 feeder for every 50 chicks
    drinkers = initial_chick_count // 50  # 1 drinker for every 50 chicks
    return feeders, drinkers


def stateholder_batch(request):
    user = request.user  # Assuming the user is logged in
    chick_batches = user.chick_batches.all().order_by('-batch_date')

    # Prepare to store batch-wise feeders and drinkers
    batch_info = []

    for batch in chick_batches:
        initial_chick_count = batch.initial_chick_count
        feeders, drinkers = calculate_feeders_and_drinkers(initial_chick_count)
        batch_info.append({
            'batch': batch,
            'initial_chick_count': initial_chick_count,
            'feeders_required': feeders,
            'drinkers_required': drinkers
        })

    total_chick_count = sum(
        batch.initial_chick_count for batch in chick_batches)
    context = {
        'batch_info': batch_info,  # Updated to pass batch information
        'total_chick_count': total_chick_count,
        'user_data': user
    }
    return render(request, 'stakeholderbatch.html', context)


def update_chick_count(request, id):
    if request.method == 'POST':
        try:
            # Get the current logged-in user
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect(reverse('stakeholderuserprofile', args=[id]))

        # Get chick count and other details from the form
        initial_chick_count = request.POST.get('initial_chick_count')
        batch_type = request.POST.get('batch_type')
        batch_size = request.POST.get('batch_size')
        price_per_kg = request.POST.get('price_per_kg')
        price_per_batch = request.POST.get('price_per_batch')

        # Validate initial chick count
        try:
            initial_chick_count = int(initial_chick_count)
            if initial_chick_count < 0:
                raise ValueError("Chick count cannot be negative.")
        except ValueError:
            messages.error(request, "Invalid chick count value.")
            return redirect(reverse('stakeholderuserprofile', args=[id]))

        # Calculate coop capacity based on user's length and breadth
        coop_capacity = 0
        if user.length and user.breadth:
            sqr_feet = user.length * user.breadth
            coop_capacity = sqr_feet * 4  # 4 birds per sq ft
        else:
            messages.error(request, "Please ensure that the coop's length and breadth are provided.")
            return redirect(reverse('stakeholderuserprofile', args=[id]))

        # Validate that the entered chick count does not exceed the coop capacity
        if initial_chick_count > coop_capacity:
            messages.error(request, f"You can't add more than {coop_capacity} birds for the current coop size.")
            return redirect(reverse('stakeholderuserprofile', args=[id]))

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
        return redirect('stakeholderuser')

    # If not POST, redirect back to the user profile
    return redirect(reverse('stakeholderuserprofile', args=[id]))
def feed_request(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'feed_request.html')


def vaccination(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'vaccinations.html', {'user': user})


@login_required  # Ensure only logged-in users can add daily data
def add_daily_data(request):
    selected_batch = None
    initial_alive_count = 0
    updated_alive_count = 0
    updated_mortality_count = 0

    # Filter batches based on the logged-in user
    all_batches = ChickBatch.objects.filter(user=request.user)

    # Initialize selected_batch_id from the session
    selected_batch_id = request.session.get('selected_batch', None)

    # Check if a batch was submitted and store it in the session
    if request.method == 'POST':
        selected_batch_id = request.POST.get('batch')
        # Store the selected batch ID in the session
        request.session['selected_batch'] = selected_batch_id

        # Handle saving daily data
        date_list = request.POST.getlist('date[]')
        sick_chicks_list = request.POST.getlist('sick_chicks[]')
        mortality_count_list = request.POST.getlist('mortality_count[]')
        feed_uplifted_list = request.POST.getlist('feed_uplifted[]')
        water_consumption_list = request.POST.getlist('water_consumption[]')
        weight_gain_list = request.POST.getlist('weight_gain[]')
        temperature_list = request.POST.getlist('temperature[]')

        # Get the selected batch object
        selected_batch = get_object_or_404(ChickBatch, id=selected_batch_id)

        # Initialize the previous day's alive count
        previous_day_data = DailyData.objects.filter(
            batch=selected_batch).order_by('-date').first()
        initial_alive_count = selected_batch.initial_chick_count

        # Loop through submitted daily entries
        for i in range(len(date_list)):
            date = date_list[i]
            sick_chicks = int(
                sick_chicks_list[i]) if sick_chicks_list[i] else 0
            mortality_count = int(
                mortality_count_list[i]) if mortality_count_list[i] else 0
            feed_uplifted = float(
                feed_uplifted_list[i]) if feed_uplifted_list[i] else 0.0
            water_consumption = float(
                water_consumption_list[i]) if water_consumption_list[i] else 0.0
            weight_gain = float(
                weight_gain_list[i]) if weight_gain_list[i] else 0.0
            temperature = float(
                temperature_list[i]) if temperature_list[i] else 0.0

            # Validation checks
            if sick_chicks < 0 or feed_uplifted < 0 or water_consumption < 0 or weight_gain < 0 or mortality_count < 0:
                messages.error(request, "Input values cannot be negative.")
                return redirect('add_daily_data')

            # Calculate updated alive count before checking mortality
            updated_alive_count = initial_alive_count - updated_mortality_count

            # Check if mortality count exceeds updated alive count or initial chick count
            if mortality_count > updated_alive_count:
                messages.error(
                    request, "Mortality count cannot exceed the updated alive count.")
                return redirect('add_daily_data')
            if mortality_count > initial_alive_count:
                messages.error(
                    request, "Mortality count cannot exceed the initial chick count.")
                return redirect('add_daily_data')

            # Check if a record already exists for the same batch and date
            existing_record = DailyData.objects.filter(
                batch=selected_batch, date=date).exists()
            if existing_record:
                messages.error(request, f"Data for {
                               date} already exists for this batch.")
                return redirect('add_daily_data')  # Redirect back to the form

            # Calculate alive_count based on previous day's data
            if previous_day_data:
                alive_count = previous_day_data.alive_count - mortality_count
            else:
                alive_count = initial_alive_count - mortality_count

            # Ensure alive_count is not negative
            if alive_count < 0:
                messages.error(
                    request, "Calculated alive count cannot be negative.")
                return redirect('add_daily_data')

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
                batch=selected_batch, date=date).first()

        messages.success(request, 'Daily data has been saved successfully.')
        return redirect('add_daily_data')  # Replace with your actual view name

    # Get the selected batch from the session if exists
    if selected_batch_id:
        selected_batch = get_object_or_404(ChickBatch, id=selected_batch_id)
        updated_mortality_count = DailyData.objects.filter(batch=selected_batch).aggregate(
            Sum('mortality_count'))['mortality_count__sum'] or 0
        # Get initial chick count again
        initial_alive_count = selected_batch.initial_chick_count
        updated_alive_count = initial_alive_count - updated_mortality_count

    return render(request, 'daily_batch.html', {
        'all_batches': all_batches,
        'selected_batch': selected_batch,
        'initial_chick_count': initial_alive_count,
        'updated_alive_count': updated_alive_count,
        'updated_mortality_count': updated_mortality_count,
    })


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
    selected_category = request.GET.get('category')
    min_value = request.GET.get('min_value')
    max_value = request.GET.get('max_value')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Validate start_date and end_date
    try:
        if start_date and end_date:
            start_date_obj = timezone.datetime.strptime(
                start_date, '%Y-%m-%d').date()
            end_date_obj = timezone.datetime.strptime(
                end_date, '%Y-%m-%d').date()

            if start_date_obj < batch.batch_date:
                raise ValueError(
                    f"Start date cannot be before the batch start date ({batch.batch_date}).")
            if end_date_obj < batch.batch_date:
                raise ValueError(
                    f"End date cannot be before the batch start date ({batch.batch_date}).")
    except ValueError as e:
        error_message = str(e)
        start_date = end_date = None  # Reset invalid dates

    # Check for negative min_value and max_value
    if (min_value and int(min_value) < 0) or (max_value and int(max_value) < 0):
        error_message = "Minimum and maximum values cannot be negative."
        min_value = max_value = None  # Reset invalid values

    # Fetch daily data for the batch
    daily_data_records = DailyData.objects.filter(batch=batch).order_by('date')

    # Apply date filtering
    if start_date and end_date:
        daily_data_records = daily_data_records.filter(
            date__range=[start_date, end_date])

    # Apply category filtering with range
    if selected_category in ['weight_gain', 'sick_chicks', 'mortality_count']:
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
        total_sick_chicks=Sum('sick_chicks'),
        total_weight_gain=Sum('weight_gain'),
        total_feed_uplifted=Sum('feed_uplifted'),
        total_water_consumption=Sum('water_consumption'),
        total_mortality_count=Sum('mortality_count'),
        average_temperature=Avg('temperature')
    )

    # Implement pagination
    paginator = Paginator(daily_data_records, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Choose the form based on the batch status
    if batch.batch_status == 'completed':
        form_class = CompletedBatchUpdateForm
    else:
        form_class = ChickenBatchForm

    if request.method == 'POST':
        form = form_class(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            # Redirect to a page that displays the batch details
            return redirect('list_daily_data', batch_id=batch.id)
    else:
        form = form_class(instance=batch)
    # Prepare context
    context = {
        'batch': batch,
        'form': form,
        'daily_data_records': page_obj,
        'selected_category': selected_category,
        'min_value': min_value,
        'max_value': max_value,
        'start_date': start_date,
        'end_date': end_date,
        'total_sick_chicks': total_metrics.get('total_sick_chicks', 0),
        'total_weight_gain': total_metrics.get('total_weight_gain', 0),
        'total_feed_uplifted': total_metrics.get('total_feed_uplifted', 0),
        'total_water_consumption': total_metrics.get('total_water_consumption', 0),
        'average_temperature': total_metrics.get('average_temperature', 0),
        'total_mortality_count': total_metrics.get('total_mortality_count', 0),
        'error_message': error_message,
    }

    return render(request, 'list_daily_data.html', context)


def edit_daily_data(request, id):
    # Fetch the specific record or return 404 if not found
    daily_data = get_object_or_404(DailyData, id=id)

    if request.method == 'POST':
        # Bind data to the form to process user input
        form = DailyDataForm(request.POST, instance=daily_data)
        if form.is_valid():
            form.save()  # Save changes
            # Redirect back to the list page
            return redirect('list_daily_data', batch_id=daily_data.batch.id)
    else:
        # Display the form with pre-filled data
        form = DailyDataForm(instance=daily_data)

    # Pass the form to the template
    return render(request, 'edit_daily_data.html', {'form': form})


def delete_daily_data(request, daily_data_id):
    daily_data_entry = get_object_or_404(DailyData, id=daily_data_id)

    # Get the batch ID to redirect to the correct page
    batch_id = daily_data_entry.batch_id  # Get the batch ID from the related batch

    daily_data_entry.delete()
    messages.success(request, 'Daily data entry deleted successfully.')

    # Redirect to the list with the batch ID
    return redirect('list_daily_data', batch_id=batch_id)


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

    if request.method == 'POST':
        form = DailyComparisonForm(request.POST, user=request.user)
        if form.is_valid():
            current_batch = form.cleaned_data['current_batch']
            past_batch = form.cleaned_data['past_batch']
            compare_day = int(form.cleaned_data['compare_day'])

            # Calculate the date for the selected day
            current_day_date = current_batch.batch_date + \
                timedelta(days=compare_day - 1)
            past_day_date = past_batch.batch_date + \
                timedelta(days=compare_day - 1)

            # Fetch the daily data
            current_day_data = DailyData.objects.filter(
                batch=current_batch, date=current_day_date).first()
            past_day_data = DailyData.objects.filter(
                batch=past_batch, date=past_day_date).first()

            # Extract data or set to 0 if not available
            current_feed_uplifted = current_day_data.feed_uplifted if current_day_data else 0
            current_weight_gain = current_day_data.weight_gain if current_day_data else 0
            current_water_consumption = current_day_data.water_consumption if current_day_data else 0

            past_feed_uplifted = past_day_data.feed_uplifted if past_day_data else 0
            past_weight_gain = past_day_data.weight_gain if past_day_data else 0
            past_water_consumption = past_day_data.water_consumption if past_day_data else 0

            # Calculate percentages (avoid division by zero)
            if current_feed_uplifted + past_feed_uplifted > 0:
                feed_uplifted_percentage = (current_feed_uplifted /
                                            (current_feed_uplifted + past_feed_uplifted)) * 100

            if current_weight_gain + past_weight_gain > 0:
                weight_gain_percentage = (current_weight_gain /
                                          (current_weight_gain + past_weight_gain)) * 100

            if current_water_consumption + past_water_consumption > 0:
                water_consumption_percentage = (current_water_consumption /
                                                (current_water_consumption + past_water_consumption)) * 100

    else:
        form = DailyComparisonForm(user=request.user)

    return render(request, 'daily_feed_summary.html', {
        'form': form,
        'current_batch': current_batch,
        'past_batch': past_batch,
        'compare_day': compare_day,
        'current_feed_uplifted': current_feed_uplifted,
        'current_weight_gain': current_weight_gain,
        'current_water_consumption': current_water_consumption,
        'past_feed_uplifted': past_feed_uplifted,
        'past_weight_gain': past_weight_gain,
        'past_water_consumption': past_water_consumption,
        'feed_uplifted_percentage': feed_uplifted_percentage,
        'weight_gain_percentage': weight_gain_percentage,
        'water_consumption_percentage': water_consumption_percentage,
    })


def batch_feed_summary(request):
    if request.method == 'POST':
        form = BatchSelectionForm(request.POST, user=request.user)
        if form.is_valid():
            selected_batch = form.cleaned_data['batch']

            # Get daily data for the selected batch
            daily_data = DailyData.objects.filter(
                batch=selected_batch).order_by('-date')

            # Prepare data for the chart and table
            dates = [data.date.strftime('%Y-%m-%d')
                     for data in daily_data]  # Dates for the x-axis
            # Daily feed uplifted
            daily_feed_uplifted = [data.feed_uplifted for data in daily_data]
            # Weight gain per day
            total_weight_gain = [data.weight_gain for data in daily_data]

            # Calculate total feed used and total weight gain
            total_feed_used = sum(daily_feed_uplifted)
            total_weight_gain_sum = sum(total_weight_gain)

            # Prepare data for the table
            daily_data_for_table = zip(
                dates, daily_feed_uplifted, total_weight_gain)

            # Pass data to the template
            return render(request, 'batch_feed_summary.html', {
                'form': form,
                'selected_batch': selected_batch,
                'dates': dates,
                'daily_feed_uplifted': daily_feed_uplifted,
                'total_weight_gain': total_weight_gain,
                'total_feed_used': total_feed_used,
                'total_weight_gain': total_weight_gain_sum,
                'daily_data': daily_data_for_table,  # Data for the table
            })
    else:
        form = BatchSelectionForm(user=request.user)

    return render(request, 'batch_feed_summary.html', {'form': form})


def feed_dashboard_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # For debugging purposes, you can print the user object to see if it's retrieved correctly
    print(f"User: {user.email}, ID: {user.id}")

    return render(request, 'feed_dashboard.html', {'user': user})


def supplier_list(request):
    """Display the list of suppliers."""
    suppliers = Supplier.objects.all()  # Fetch all suppliers from the database
    return render(request, 'supplier_list_stakeholder.html', {'suppliers': suppliers})

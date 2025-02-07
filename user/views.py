from hoteldetails.models import Order
from django.contrib.auth.decorators import login_required
from .forms import SupplierForm
from .models import Supplier
from .models import User
from django.shortcuts import get_object_or_404, redirect
from datetime import date
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Sum

from stakeholder.models import ChickBatch, DailyData,Farm
from .forms import CustomUserCreationForm, EmailAuthenticationForm
from .models import UserType, User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import pandas as pd
from math import floor
from .models import WasteManagementResource, DailyTip
from django.db import models
from django.views.decorators.http import require_http_methods
from .models import Vaccine, VaccinationRecord
from django.http import JsonResponse
from datetime import datetime


def register(request):
    user_type_param = request.GET.get('user_type')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            print(user)
            # Get the selected user type
            user_type = UserType.objects.get(name=user_type_param)
            print(user_type)

            # Set is_active based on user type
            if user_type.name.lower() == 'admin':
                user.is_active = True  # Admins are active by default
            else:
                user.is_active = False  # Stakeholders and customers are inactive by default

            # Save user and log them in if active
            user.user_type = user_type
            user.save()
            if user.is_active:
                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')
                # Adjust this to your homepage or dashboard
                return redirect('home')

            messages.info(request, 'Your account will be activated soon.')
            # Adjust to a relevant page for inactive users
            return redirect('/')

        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = 'login.html'  # Specify your template
    redirect_authenticated_user = True  # Redirect if user is already logged in
    # Where to redirect after successful login
    success_url = reverse_lazy('home')

    def get_success_url(self):  # checking for which type of user after login
        user = self.request.user
        if user.user_type != None and hasattr(user, 'user_type') and user.user_type.name.lower() == 'stakeholder':
            return reverse_lazy('stakeholder')

        # elif user.expiry_date and user.expiry_date < date.today():
        #     # Redirect the user to an 'expiry notification' page if the certificate has expired
        #     return reverse_lazy('expiry_notification')

        elif user.user_type != None and user.user_type.name.lower() == 'admin':
            return reverse_lazy('admindash')
        elif user.user_type != None and user.user_type.name.lower() == 'customer':
            return reverse_lazy('hoteldashboard')
        return self.success_url
from django.utils import timezone
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

def admindash(request):
    # Fetching the usertype with name 'Stakeholder'
    stakeholder_user_type = UserType.objects.get(name='Stakeholder')

    # Counting total stakeholders
    total_stakeholders = User.objects.filter(user_type=stakeholder_user_type).count()

    # Counting active stakeholders
    active_stakeholders = User.objects.filter(
        user_type=stakeholder_user_type, is_active=True).count()

    # Fetching the usertype with name 'Customer'
    customer_user_type = UserType.objects.get(name='Customer')
    customer_count = User.objects.filter(user_type=customer_user_type).count()

    # Counting total farms (which are essentially stakeholders)
    total_farm = total_stakeholders
    total_one_kg = ChickBatch.objects.aggregate(total_one_kg=Sum('one_kg_count'))['total_one_kg'] or 0
    total_two_kg = ChickBatch.objects.aggregate(total_two_kg=Sum('two_kg_count'))['total_two_kg'] or 0
    total_three_kg = ChickBatch.objects.aggregate(total_three_kg=Sum('three_kg_count'))['total_three_kg'] or 0
    available_chicks_by_type = ChickBatch.objects.values('batch_type').annotate(total_available_chicks=Sum('available_chickens'))

    # Counting active farms (which are essentially active stakeholders)
    farmactive_count = active_stakeholders

    # Fetch today's orders
    today = timezone.now().date()
    todays_orders = Order.objects.filter(order_date__date=today)

    # Fetching today's sales data
    todays_sales = Order.objects.filter(order_date__date=today).aggregate(
        total_one_kg=Sum('one_kg_count'),
        total_two_kg=Sum('two_kg_count'),
        total_three_kg=Sum('three_kg_count')
    )

    # Fetching this week's sales data
    start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + timedelta(days=6)  # End of the week (Sunday)
    weekly_sales = Order.objects.filter(order_date__date__range=[start_of_week, end_of_week]).aggregate(
        total_one_kg=Sum('one_kg_count'),
        total_two_kg=Sum('two_kg_count'),
        total_three_kg=Sum('three_kg_count')
    )

    # Fetching this month's sales data
    start_of_month = today.replace(day=1)  # Start of the month (1st day)
    end_of_month = start_of_month.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)  # End of the month
    monthly_sales = Order.objects.filter(order_date__date__range=[start_of_month, end_of_month]).aggregate(
        total_one_kg=Sum('one_kg_count'),
        total_two_kg=Sum('two_kg_count'),
        total_three_kg=Sum('three_kg_count')
    )

    return render(request, 'dashboard.html', {
        'stakeholder_count': total_stakeholders,
        'customer_count': customer_count,
        'farmactive_count': farmactive_count,
        'total_farm': total_farm,
        'total_one_kg': total_one_kg,
        'total_two_kg': total_two_kg,
        'total_three_kg': total_three_kg,
        'available_chicks_by_type': available_chicks_by_type,
        'todays_sales_data': [todays_sales],
        'weekly_sales_data': [weekly_sales],
        'monthly_sales_data': [monthly_sales],
    })




def stakeholderuser(request):
    # fetching the usertype with name stakeholder
    user_type = UserType.objects.get(name='Stakeholder')
    users = User.objects.filter(user_type=user_type)
    context = {'users': users}
    return render(request, 'stakeholderuser.html', context)


def stakeholderuserprofile(request, id):
    user = User.objects.get(id=id)
    farm = Farm.objects.filter(owner=user).first()  # Get the associated farm
    chick_batches = ChickBatch.objects.filter(user=user)
    total_chick_count = chick_batches.aggregate(Sum('initial_chick_count'))['initial_chick_count__sum'] or 0

    today = date.today()
    day_expiry = None
    if farm.expiry_date:
        day_expiry = (farm.expiry_date - today).days

    # Calculate square feet based on length and breadth
    sqr_feet = 0
    if farm.length and farm.breadth:
        sqr_feet = farm.length * farm.breadth
    sqr_feet_rounded = round(sqr_feet, 0)

    # Calculate number of birds that can be accommodated
    birds_per_square_feet = 2
    birds_can_accommodate = floor(sqr_feet * birds_per_square_feet)

    if request.method == 'POST':
        if not user.is_active:
            messages.error(request, "You cannot add chicks because the user account is disabled.")
            return redirect('stakeholderuserprofile', id=id)

        initial_chick_count = request.POST.get('initial_chick_count')
        batch_type = request.POST.get('batch_type')  # Get the type of chickens
        price_per_kg = request.POST.get('price_per_kg')  # Get the price per kg

        # Backend validation: Chick count must not be less than zero
        try:
            initial_chick_count = int(initial_chick_count)
            if initial_chick_count < 0:
                messages.error(request, "Chick count cannot be less than zero.")
                return redirect('stakeholderuserprofile', id=id)
        except (ValueError, TypeError):
            messages.error(request, "Invalid chick count entered. Please enter a valid number.")
            return redirect('stakeholderuserprofile', id=id)

        # Save the chick count to the user's chick batches
        ChickBatch.objects.create(
            user=user,
            farm=farm,  # Associate the ChickBatch with the farm
            initial_chick_count=initial_chick_count,
            batch_type=batch_type,  # Save the type of chickens
            price_per_kg=price_per_kg  # Save the price per kg
        )
        messages.success(request, "Chick count updated successfully.")
        return redirect('stakeholderuserprofile', id=id)

    context = {
        'user': user,
        'total_chick_count': total_chick_count,
        'day_expiry': day_expiry,
        'sqr_feet': sqr_feet_rounded,
        'birds_can_accommodate': birds_can_accommodate
    }

    return render(request, 'stakeholderprofile.html', context)


def view_stakeholder_view(request, id):
    chick_batches = ChickBatch.objects.filter(
        user_id=id)  # Adjust the queryset as needed
    return render(request, 'chick_batches_list.html', {'chick_batches': chick_batches,"user":id})


def download_daily_log(request, batch_id):
    try:
        # Retrieve the DailyData records for the specific batch
        batch = ChickBatch.objects.get(id=batch_id)
        daily_data_records = DailyData.objects.filter(batch=batch)

        # Create a DataFrame for the daily log
        data = {
            'Date': [record.date for record in daily_data_records],
            'Alive Count': [record.alive_count for record in daily_data_records],
            'Sick Chicks': [record.sick_chicks for record in daily_data_records],
            'Weight Gain (g)': [record.weight_gain for record in daily_data_records],
            'Feed Uplifted (kg)': [record.feed_uplifted for record in daily_data_records],
            'Water Consumption (L)': [record.water_consumption for record in daily_data_records],
            'Temperature': [record.temperature for record in daily_data_records],
            'Mortality Count': [record.mortality_count for record in daily_data_records],
        }

        df = pd.DataFrame(data)

        # Create an HTTP response with the appropriate Excel content type
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="daily_log_{batch_id}.xlsx"'

        # Write the DataFrame to the response using ExcelWriter
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Daily Log')

        return response

    except ChickBatch.DoesNotExist:
        return HttpResponse("Batch not found", status=404)


def customeruser(request):
    # fetching the usertype with customer
    user_type = UserType.objects.get(name='Customer')
    # fetching all user that having user type as customer
    users = User.objects.filter(user_type=user_type)
    # context is using in html for rendering the data eg: user.name,user.email etc
    context = {'users': users}
    return render(request, 'customeruser.html', context)


def customeruserprofile(request, id):
    user = User.objects.get(id=id)
    orders = Order.objects.filter(user=id)
    return render(request, 'customerprofile.html', {'user': user, 'orders': orders})


@login_required
def approve_order(request, order_id):
    # Fetch the order and update its status
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # Check if the order can be fulfilled
        if not order.can_fulfill_order():
            messages.error(
                request, "Not enough chickens available to fulfill this order.")
            return redirect('customeruserprofile', id=order.user.id)

        # Confirm the order
        try:
            order.confirm_order()
            messages.success(request, "Order confirmed successfully!")
            return redirect('customeruserprofile', id=order.user.id)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('customeruserprofile', id=order.user.id)
    # Redirect back to the profile page
    return redirect('customeruserprofile', id=order.user.id)

def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        # Toggle the user's active status
        user.is_active = not user.is_active
        user.save()

        status = "enabled" if user.is_active else "disabled"
        messages.success(request, f"User has been {status} successfully.")
        if user.user_type.name.lower() == "customer":
            return redirect('customeruser')
    return redirect('stakeholderuser')


def vaccine_admin(request):
    # Assuming you're trying to retrieve a VaccineAdmin object by its ID (pk)


    return render(request, 'vaccination.html')


def feed_admin(request):
    return render(request, 'feedadmin.html')


# user/views.py


def renew_pollution_certificate(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_expiry_date = request.POST.get('expiry_date')
        if new_expiry_date:
            user.expiry_date = new_expiry_date  # Update the expiry date
            user.is_active = True  # Reactivate the user
            user.save()
            messages.success(
                request, "Pollution certificate renewed successfully.")
        else:
            messages.error(request, "Please provide a valid expiry date.")

    # Replace 'some_view' with the appropriate view name
    return redirect('stakeholder')


# user/views.py


def supplier_list(request):
    """Display the list of suppliers."""
    suppliers = Supplier.objects.all()
    return render(request, 'supplier_list.html', {'suppliers': suppliers})


def add_supplier(request):
    """Add a new supplier."""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            # Success message
            messages.success(request, 'Supplier added successfully.')
            # Redirect to supplier list after adding
            return redirect('supplier_list')
        else:
            # This part will execute if the form is not valid
            # Error message
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SupplierForm()

    return render(request, 'add_supplier.html', {'form': form})


def edit_supplier(request, supplier_id):
    """Edit an existing supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            # Redirect to supplier list after editing
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'edit_supplier.html', {'form': form})


def enable_supplier(request, supplier_id):
    """Enable a supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.is_active = True
    supplier.save()
    # Redirect to supplier list after enabling
    return redirect('supplier_list')


def disable_supplier(request, supplier_id):
    """Disable a supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.is_active = False
    supplier.save()
    # Redirect to supplier list after disabling
    return redirect('supplier_list')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Vaccine
from .forms import VaccineForm

def vaccination_main(request):
    return render(request, 'vaccination_main.html')

def manage_vaccines(request):
    """View for vaccine dashboard with CRUD operations"""
    vaccines = Vaccine.objects.all()
    total_vaccines = vaccines.count()
    
    # Get vaccination records
    vaccination_records = VaccinationRecord.objects.all()
    completed_vaccinations = vaccination_records.filter(status='completed').count()
    pending_vaccinations = vaccination_records.filter(status='pending').count()
    low_stock_count = vaccines.filter(current_stock__lt=30).count()

    upcoming_schedules = vaccination_records.filter(
        status='pending'
    ).order_by('scheduled_date')[:5]

    vaccine_stocks = [{
        'vaccine_name': vaccine.name,
        'current_stock': vaccine.current_stock,
        'max_stock': 100,  # You can adjust this or make it dynamic
        'stock_percentage': (vaccine.current_stock / 100) * 100 if vaccine.current_stock else 0,
        'status': 'LOW' if vaccine.current_stock and vaccine.current_stock < 30 else 'OK'
    } for vaccine in vaccines]

    context = {
        'total_vaccines': total_vaccines,
        'completed_vaccinations': completed_vaccinations,
        'pending_vaccinations': pending_vaccinations,
        'low_stock_count': low_stock_count,
        'upcoming_schedules': upcoming_schedules,
        'vaccine_stocks': vaccine_stocks,
        'vaccines': vaccines
    }
    
    return render(request, 'vaccine_dashboard.html', context)

@require_http_methods(["POST"])
def add_vaccine(request):
    try:
        name = request.POST.get('name').strip()
        manufacturer = request.POST.get('manufacturer').strip()
        doses_required = int(request.POST.get('doses_required'))
        interval_days = int(request.POST.get('interval_days'))
        current_stock = int(request.POST.get('current_stock', 0))

        if not all([name, manufacturer, doses_required, interval_days]):
            return JsonResponse({'success': False, 'message': 'All fields are required.'})

        vaccine = Vaccine.objects.create(
            name=name,
            manufacturer=manufacturer,
            doses_required=doses_required,
            interval_days=interval_days,
            current_stock=current_stock
        )

        return JsonResponse({
            'success': True,
            'message': 'Vaccine added successfully!',
            'vaccine': {
                'id': vaccine.id,
                'name': vaccine.name,
                'manufacturer': vaccine.manufacturer,
                'doses_required': vaccine.doses_required,
                'interval_days': vaccine.interval_days,
                'current_stock': vaccine.current_stock
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["POST"])
def edit_vaccine(request, vaccine_id):
    try:
        vaccine = get_object_or_404(Vaccine, id=vaccine_id)
        
        # Update vaccine data
        vaccine.name = request.POST.get('name').strip()
        vaccine.manufacturer = request.POST.get('manufacturer').strip()
        vaccine.doses_required = int(request.POST.get('doses_required'))
        vaccine.interval_days = int(request.POST.get('interval_days'))
        vaccine.current_stock = int(request.POST.get('current_stock', 0))

        # Update stock status based on current stock
        if vaccine.current_stock == 0:
            vaccine.stock_status = 'OUT_OF_STOCK'
        elif vaccine.current_stock < 30:
            vaccine.stock_status = 'LOW_STOCK'
        else:
            vaccine.stock_status = 'IN_STOCK'

        vaccine.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Vaccine updated successfully!',
            'vaccine': {
                'id': vaccine.id,
                'name': vaccine.name,
                'manufacturer': vaccine.manufacturer,
                'doses_required': vaccine.doses_required,
                'interval_days': vaccine.interval_days,
                'current_stock': vaccine.current_stock,
                'stock_status': vaccine.stock_status
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def delete_vaccine(request, vaccine_id):
    try:
        vaccine = get_object_or_404(Vaccine, id=vaccine_id)
        
        # Check if vaccine is in use
        if VaccinationSchedule.objects.filter(vaccine=vaccine).exists():
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete vaccine as it is associated with vaccination schedules.'
            })
            
        vaccine.delete()
        return JsonResponse({
            'success': True,
            'message': 'Vaccine deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })





def manage_records(request):
    records = VaccinationRecord.objects.all()
    return render(request, 'manage_records.html', {'records': records})

def add_record(request):
    if request.method == 'POST':
        form = VaccinationRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_records')
    else:
        form = VaccinationRecordForm()
    return render(request, 'add_record.html', {'form': form})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from stakeholder.models import ChickBatch, VaccinationSchedule
from user.models import User ,Vaccine # Replace `your_app` with the actual app name

def assign_vaccine(request):
    """
    Renders the vaccine assignment form and handles the form submission.
    """
    if request.method == 'POST':
        try:
            # Retrieve POST data
            user_id = request.POST.get('user')
            batch_id = request.POST.get('batch')
            vaccine_id = request.POST.get('vaccine')
            vaccination_date = request.POST.get('vaccination_date')

            # Validate inputs
            if not user_id or not batch_id or not vaccine_id or not vaccination_date:
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

            # Check if user exists
            user = get_object_or_404(User, id=user_id, user_type='stakeholder')  # Ensure filtering by user_type works

            # Check if batch exists and is active
            batch = get_object_or_404(ChickBatch, id=batch_id, user=user, batch_status="active")

            # Check if vaccine exists
            vaccine = get_object_or_404(Vaccine, id=vaccine_id)

            # Prevent duplicate vaccination schedules for the same batch and vaccine
            if VaccinationSchedule.objects.filter(batch=batch, vaccine=vaccine).exists():
                return JsonResponse({
                    "success": False,
                    "message": "This vaccine is already scheduled for the selected batch."
                }, status=400)

            # Create the VaccinationSchedule
            VaccinationSchedule.objects.create(
                batch=batch,
                vaccine=vaccine,
                vaccination_date=vaccination_date
            )

            # Return success response
            return JsonResponse({"success": True, "message": "Vaccine assigned successfully."})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"An unexpected error occurred: {str(e)}"}, status=500)

    # If GET request, render the form
    users = User.objects.filter(user_type='stakeholder')  # Fetch only stakeholders
    vaccines = Vaccine.objects.all()  # Fetch all vaccines
    return render(request, 'assign_vaccine.html', {
        'users': users,
        'vaccines': vaccines,
    })



def get_active_batches(request, user_id):
    """
    Returns active batches for a given stakeholder user.
    """
    try:
        # Check if the user is a stakeholder
        stakeholder = get_object_or_404(User, id=user_id, user_type='stakeholder')

        # Get active batches for the stakeholder
        active_batches = ChickBatch.objects.filter(user=stakeholder, batch_status='active')

        # Prepare the batch data for the response
        batch_data = [
            {"id": batch.id, "name": f"Batch {batch.id} - {batch.batch_date}"}
            for batch in active_batches
        ]


        return JsonResponse({"batches": batch_data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def waste_management_admin(request):
    # Get statistics for the dashboard
    resources = WasteManagementResource.objects.all()
    daily_tips = DailyTip.objects.all()
    
    context = {
        'total_resources': resources.count(),
        'active_resources': resources.filter(is_active=True).count(),
        'total_tips': daily_tips.count(),
        'active_tips': daily_tips.filter(is_active=True).count(),
        'resources': resources.order_by('-created_at')[:5],  # Latest 5 resources
        'tips': daily_tips.order_by('-created_at')[:5],     # Latest 5 tips
    }
    
    return render(request, 'waste_management_admin.html', context)


def add_resource(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        resource_type = request.POST.get('resource_type')
        file = request.FILES.get('file')
        
        WasteManagementResource.objects.create(
            title=title,
            description=description,
            resource_type=resource_type,
            file=file,
            is_active=True
        )
        
        messages.success(request, 'Resource added successfully!')
        return redirect('waste_management_admin')
    return redirect('waste_management_admin')


def add_tip(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        
        DailyTip.objects.create(
            title=title,
            content=content,
            category=category,
            is_active=True
        )
        
        messages.success(request, 'Tip added successfully!')
        return redirect('waste_management_admin')
    return redirect('waste_management_admin')


def view_resources(request):
    resources = WasteManagementResource.objects.all().order_by('-created_at')
    return render(request, 'waste_management.html', {'resources': resources, 'section': 'resources'})


def view_tips(request):
    tips = DailyTip.objects.all().order_by('-created_at')
    return render(request, 'waste_management.html', {'tips': tips, 'section': 'tips'})


# views.py
from django.shortcuts import render

def get_vaccine(request, vaccine_id):
    try:
        print(f"Getting vaccine with ID: {vaccine_id}")  # Debug log
        vaccine = get_object_or_404(Vaccine, id=vaccine_id)
        print(f"Found vaccine: {vaccine.name}")  # Debug log
        
        response_data = {
            'success': True,
            'vaccine': {
                'name': vaccine.name,
                'manufacturer': vaccine.manufacturer,
                'doses_required': vaccine.doses_required,
                'interval_days': vaccine.interval_days,
                'current_stock': vaccine.current_stock,
                'stock_status': vaccine.stock_status,
                'expiry_date': vaccine.expiry_date.strftime('%Y-%m-%d') if vaccine.expiry_date else ''
            }
        }
        print(f"Response data: {response_data}")  # Debug log
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Error in get_vaccine: {str(e)}")  # Debug log
        return JsonResponse({
            'success': False,
            'message': f"Error retrieving vaccine: {str(e)}"
        })

def vaccine_stock_level(request):
    vaccines = Vaccine.objects.all()
    return render(request, 'vaccine_stock_level.html', {'vaccines': vaccines})

@require_http_methods(["POST"])
def update_stock(request, vaccine_id):
    try:
        print(f"Updating stock for vaccine ID: {vaccine_id}")  # Debug log
        print(f"POST data: {request.POST}")  # Debug log
        
        vaccine = get_object_or_404(Vaccine, id=vaccine_id)
        
        # Get and validate current_stock
        try:
            current_stock = int(request.POST.get('current_stock', 0))
            if current_stock < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Stock level cannot be negative'
                })
        except ValueError as e:
            print(f"Stock validation error: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'message': 'Invalid stock value'
            })
        
        # Update vaccine stock
        vaccine.current_stock = current_stock
        
        # Update stock status
        if current_stock == 0:
            vaccine.stock_status = 'OUT_OF_STOCK'
        elif current_stock < 30:
            vaccine.stock_status = 'LOW_STOCK'
        else:
            vaccine.stock_status = 'IN_STOCK'
            
        # Update expiry date if provided
        expiry_date = request.POST.get('expiry_date')
        if expiry_date:
            try:
                vaccine.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError as e:
                print(f"Date validation error: {str(e)}")  # Debug log
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid expiry date format'
                })
        
        vaccine.save()
        print("Stock updated successfully")  # Debug log
        
        return JsonResponse({
            'success': True,
            'message': 'Stock updated successfully',
            'vaccine': {
                'id': vaccine.id,
                'current_stock': current_stock,
                'stock_status': vaccine.stock_status,
                'expiry_date': vaccine.expiry_date.strftime('%Y-%m-%d') if vaccine.expiry_date else None
            }
        })
        
    except Exception as e:
        print(f"Error updating stock: {str(e)}")  # Debug log
        return JsonResponse({
            'success': False,
            'message': f'Error updating stock: {str(e)}'
        })



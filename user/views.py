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

from django.core.exceptions import ValidationError
from decimal import Decimal  # Add this import at the top
from django.db import transaction
from django.db import connection
from django.db.models import Count, Avg, F, Q, Max, Min, Case, When, FloatField, StdDev
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from .forms import ContractForm  # Import the ContractForm
from django.template.loader import render_to_string
# from weasyprint import HTML  # Assuming you're using WeasyPrint for PDF generation

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import ChatRoom, ChatMessage
from django.db.models import (
    F, Count, Avg, Sum, Q, 
    ExpressionWrapper, DurationField,
    IntegerField
)
from django.db.models.functions import Coalesce, ExtractDay

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


@transaction.atomic
def stakeholderuserprofile(request, id):
    user = User.objects.get(id=id)
    farm = Farm.objects.filter(owner=user).first()
    
    # Calculate all required context data
    chick_batches = ChickBatch.objects.filter(user=user)
    total_chick_count = chick_batches.aggregate(Sum('initial_chick_count'))['initial_chick_count__sum'] or 0

    today = date.today()
    day_expiry = None
    if farm and farm.expiry_date:
        day_expiry = (farm.expiry_date - today).days

    # Calculate square feet based on length and breadth
    sqr_feet = 0
    if farm and farm.length and farm.breadth:
        sqr_feet = farm.length * farm.breadth
    sqr_feet_rounded = round(sqr_feet, 0)

    # Calculate number of birds that can be accommodated
    birds_per_square_feet = 2
    birds_can_accommodate = floor(sqr_feet * birds_per_square_feet)

    if request.method == 'POST':
        try:
            # Print all POST data
            print("POST data received:", request.POST)
            
            batch_type = request.POST.get('batch_type')
            if not batch_type:
                raise ValueError("Batch type is required")

            try:
                initial_chick_count = int(request.POST.get('initial_chick_count', 0))
                price_per_kg = Decimal(request.POST.get('price_per_kg', 0))
                total_feed_sacks = int(request.POST.get('total_feed_sacks', 0))
                starter_feed_sacks = int(request.POST.get('starter_feed_sacks', 0))
                
                # Print processed values
                print("Processed values:", {
                    'batch_type': batch_type,
                    'initial_chick_count': initial_chick_count,
                    'price_per_kg': price_per_kg,
                    'total_feed_sacks': total_feed_sacks,
                    'starter_feed_sacks': starter_feed_sacks
                })

            except (TypeError, ValueError) as e:
                print(f"Form data: {request.POST}")
                raise ValueError(f"Invalid number format: {str(e)}")

            with transaction.atomic():
                batch = ChickBatch.objects.create(
                    user=user,
                    farm=farm,
                    batch_type=batch_type,
                    initial_chick_count=initial_chick_count,
                    price_per_kg=price_per_kg,
                    total_feed_sacks=total_feed_sacks,
                    starter_feed_sacks=starter_feed_sacks,
                    available_chickens=initial_chick_count,
                    remaining_feed_sacks=total_feed_sacks
                )
                
                # Verify the saved data
                saved_batch = ChickBatch.objects.get(id=batch.id)
                print("Saved batch data:", {
                    'id': saved_batch.id,
                    'starter_feed_sacks': saved_batch.starter_feed_sacks,
                    'total_feed_sacks': saved_batch.total_feed_sacks
                })

                messages.success(request, "Batch created successfully with feed assignments.")

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            print(f"Error: {str(e)}")
            messages.error(request, f"Error creating batch: {str(e)}")
        
        return redirect('stakeholderuserprofile', id=id)

    context = {
        'user': user,
        'farm': farm,
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
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # Debug prints
        print(f"Order quantities - 1kg: {order.one_kg_count}, 2kg: {order.two_kg_count}, 3kg: {order.three_kg_count}")
        print(f"Batch quantities - 1kg: {order.batch.one_kg_count}, 2kg: {order.batch.two_kg_count}, 3kg: {order.batch.three_kg_count}")
        
        # Check if the order can be fulfilled
        if not order.can_fulfill_order():
            messages.error(
                request, f"Not enough chickens available. Required: 1kg:{order.one_kg_count}, 2kg:{order.two_kg_count}, 3kg:{order.three_kg_count}. Available: 1kg:{order.batch.one_kg_count}, 2kg:{order.batch.two_kg_count}, 3kg:{order.batch.three_kg_count}")
            return redirect('customeruserprofile', id=order.user.id)

        # Confirm the order
        try:
            order.confirm_order()
            messages.success(request, "Order confirmed successfully!")
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('customeruserprofile', id=order.user.id)
    
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

# Remove or comment out this function
# def vaccination_main(request):
#     return render(request, 'vaccination_main.html')

@login_required
def manage_vaccines(request):
    # Group vaccines by vaccination day
    vaccines = {
        7: Vaccine.objects.filter(vaccination_day=7),
        14: Vaccine.objects.filter(vaccination_day=14),
        21: Vaccine.objects.filter(vaccination_day=21)
    }
    
    context = {
        'day_7_vaccines': vaccines[7],
        'day_14_vaccines': vaccines[14],
        'day_21_vaccines': vaccines[21],
        'form': VaccineForm()
    }
    return render(request, 'manage_vaccines.html', context)

@login_required
@require_http_methods(["POST"])
def add_vaccine(request):
    try:
        print("POST data:", request.POST)  # Debug print
        form = VaccineForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug print
            vaccine = form.save()
            return JsonResponse({
                'success': True,
                'vaccine': {
                    'id': vaccine.id,
                    'name': vaccine.name,
                    'manufacturer': vaccine.manufacturer,
                    'batch_number': vaccine.batch_number,
                    'vaccination_day': vaccine.get_vaccination_day_display(),
                    'current_stock': vaccine.current_stock,
                    'stock_status': vaccine.stock_status
                }
            })
        else:
            print("Form errors:", form.errors)  # Debug print
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        print("Exception:", str(e))  # Debug print
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def edit_vaccine(request, vaccine_id):
    try:
        vaccine = get_object_or_404(Vaccine, id=vaccine_id)
        form = VaccineForm(request.POST, instance=vaccine)
        
        if form.is_valid():
            vaccine = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Vaccine updated successfully',
                'vaccine': {
                    'id': vaccine.id,
                    'name': vaccine.name,
                    'manufacturer': vaccine.manufacturer,
                    'batch_number': vaccine.batch_number,
                    'vaccination_day': vaccine.get_vaccination_day_display(),
                    'current_stock': vaccine.current_stock,
                    'stock_status': vaccine.stock_status
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

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

@login_required
def assign_vaccine(request):
    if request.method == 'POST':
        vaccine_id = request.POST.get('vaccine')
        batch_id = request.POST.get('batch')
        scheduled_date = request.POST.get('scheduled_date')
        
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
            batch = ChickBatch.objects.get(id=batch_id)
            
            # Check if we have enough stock
            if vaccine.current_stock <= 0:
                messages.error(request, 'Not enough vaccine stock available')
                return redirect('manage_vaccines')
            
            # Create vaccination schedule
            VaccinationSchedule.objects.create(
                vaccine=vaccine,
                batch=batch,
                scheduled_date=scheduled_date
            )
            
            # Reduce vaccine stock
            vaccine.current_stock -= 1  # or however many doses are needed
            vaccine.save()
            
            messages.success(request, 'Vaccination scheduled successfully')
            return redirect('manage_vaccines')
            
        except (Vaccine.DoesNotExist, ChickBatch.DoesNotExist):
            messages.error(request, 'Invalid vaccine or batch selected')
            return redirect('manage_vaccines')
    
    return redirect('manage_vaccines')



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
        vaccine = get_object_or_404(Vaccine, id=vaccine_id)
        return JsonResponse({
            'success': True,
            'vaccine': {
                'name': vaccine.name,
                'manufacturer': vaccine.manufacturer,
                'batch_number': vaccine.batch_number,
                'vaccination_day': vaccine.vaccination_day,
                'current_stock': vaccine.current_stock,
                'minimum_stock_level': vaccine.minimum_stock_level,
                'doses_required': vaccine.doses_required,
                'expiry_date': vaccine.expiry_date.strftime('%Y-%m-%d') if vaccine.expiry_date else '',
                'notes': vaccine.notes
            }
        })
    except Vaccine.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Vaccine not found'})

@login_required
def vaccine_stock_level(request):
    vaccines = Vaccine.objects.all()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        vaccine_data = [{
            'id': vaccine.id,
            'name': vaccine.name,
            'manufacturer': vaccine.manufacturer,
            'batch_number': vaccine.batch_number,
            'vaccination_day': vaccine.get_vaccination_day_display(),
            'current_stock': vaccine.current_stock,
            'minimum_stock_level': vaccine.minimum_stock_level,
            'stock_status': vaccine.stock_status
        } for vaccine in vaccines]
        return JsonResponse({'vaccines': vaccine_data})
    # If regular request, return HTML
    return render(request, 'vaccine_stock_level.html', {'vaccines': vaccines})

@login_required
def vaccine_dashboard(request):
    vaccines = Vaccine.objects.all()
    context = {
        'vaccines': vaccines,
        'day_7_vaccines': vaccines.filter(vaccination_day=7),
        'day_14_vaccines': vaccines.filter(vaccination_day=14),
        'day_21_vaccines': vaccines.filter(vaccination_day=21),
    }
    return render(request, 'vaccine_dashboard.html', context)

@login_required
@require_http_methods(["POST"])
def restock_vaccine(request, vaccine_id):
    try:
        vaccine = get_object_or_404(Vaccine, id=vaccine_id)
        restock_amount = int(request.POST.get('restock_amount', 0))
        batch_number = request.POST.get('batch_number')
        expiry_date = request.POST.get('expiry_date')
        
        if restock_amount <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Restock amount must be positive'
            })
        
        # Update vaccine stock
        vaccine.current_stock += restock_amount
        
        if batch_number:
            vaccine.batch_number = batch_number
        if expiry_date:
            vaccine.expiry_date = expiry_date
            
        vaccine.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Added {restock_amount} units to stock',
            'new_stock': vaccine.current_stock,
            'stock_status': vaccine.stock_status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def vaccine_table(request):
    vaccines = Vaccine.objects.all().values(
        'id',
        'name',
        'manufacturer',
        'batch_number',
        'vaccination_day',
        'doses_required',
        'current_stock',
        'minimum_stock_level',
        'stock_status'
    )
    context = {
        'vaccines': list(vaccines)
    }
    return render(request, 'vaccine_table.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user.models import FeedStock
from .forms import FeedStockForm
from decimal import Decimal

@login_required
def feed_manage(request):
    """Feed management view"""
    feed_stocks = FeedStock.objects.all()

    if request.method == 'POST':
        try:
            # Get form data
            feed_type = request.POST.get('feed_type')
            number_of_sacks = request.POST.get('number_of_sacks')
            price_per_sack = request.POST.get('price_per_sack')
            minimum_sacks = request.POST.get('minimum_sacks')
            
            # Print debug information
            print("Received data:", {
                'feed_type': feed_type,
                'number_of_sacks': number_of_sacks,
                'price_per_sack': price_per_sack,
                'minimum_sacks': minimum_sacks
            })
            
            # Create form instance with data
            form = FeedStockForm(request.POST)
            
            if form.is_valid():
                feed_stock = form.save()
                messages.success(request, 'Feed stock added successfully!')
                return redirect('feed_manage')
            else:
                print("Form errors:", form.errors)
                error_messages = []
                for field, errors in form.errors.items():
                    error_messages.append(f"{field}: {', '.join(errors)}")
                messages.error(request, f"Error in form: {'; '.join(error_messages)}")
        except Exception as e:
            messages.error(request, f'Error saving feed stock: {str(e)}')
    else:
        form = FeedStockForm()

    context = {
        'feed_stocks': feed_stocks,
        'form': form,
        'title': 'Feed Management'
    }
    return render(request, 'stakeholder/feed_manage.html', context)



from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from datetime import datetime, timedelta
from django.utils import timezone
import pandas as pd
import json

def order_analytics(request):
    try:
        # Basic Order Statistics
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('price'))['total'] or 0

        # Orders by Weight Category
        weight_distribution = {
            '1KG': Order.objects.aggregate(total=Sum('one_kg_count'))['total'] or 0,
            '2KG': Order.objects.aggregate(total=Sum('two_kg_count'))['total'] or 0,
            '3KG': Order.objects.aggregate(total=Sum('three_kg_count'))['total'] or 0
        }

        # Simple date-based aggregation without timezone complications
        orders_by_date = Order.objects.extra(
            select={'order_day': 'DATE(order_date)'}
        ).values('order_day').annotate(
            revenue=Sum('price'),
            count=Count('id')
        ).order_by('order_day')

        # Prepare data for charts
        dates = []
        revenues = []
        for order in orders_by_date:
            if order['order_day']:
                dates.append(order['order_day'].strftime('%Y-%m-%d'))
                revenues.append(float(order['revenue'] or 0))

        # Payment Methods
        payment_methods = Order.objects.values('payment_method').annotate(
            count=Count('id')
        ).order_by('-count')

        payment_labels = [p['payment_method'] for p in payment_methods]
        payment_data = [p['count'] for p in payment_methods]

        # Customer Frequency
        customer_frequency = Order.objects.values(
            'user__full_name'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('price')
        ).order_by('-order_count')[:10]

        context = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'weight_distribution': weight_distribution,
            'daily_orders': json.dumps(dates),
            'daily_revenue': json.dumps(revenues),
            'payment_labels': json.dumps(payment_labels),
            'payment_data': json.dumps(payment_data),
            'customer_frequency': customer_frequency,
        }

        return render(request, 'order_analytics.html', context)

    except Exception as e:
        print(f"Error in order_analytics: {str(e)}")  # Debug print
        messages.error(request, f"Error generating analytics: {str(e)}")
        return redirect('admindash')
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required

@login_required
def farm_analytics_dashboard(request):
    try:
        # Get all farms with basic batch counts
        farms = Farm.objects.annotate(
            total_batches=Count('chick_batches'),
            active_batches=Count('chick_batches', 
                filter=Q(chick_batches__batch_status='active')),
            completed_batches=Count('chick_batches', 
                filter=Q(chick_batches__batch_status='completed'))
        )

        context = {
            'farms': farms,
            'total_farms': farms.count(),
        }

        return render(request, 'farm_analytics_dashboard.html', context)

    except Exception as e:
        print(f"Error in farm analytics: {str(e)}")
        messages.error(request, f"Error generating farm analytics: {str(e)}")
        return redirect('admindash')
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Contract


@login_required
def contract_dashboard(request):
    context = {
        'total_contracts': Contract.objects.count(),
        'pending_signatures': Contract.objects.filter(status='Pending').count(),
        'signed_contracts': Contract.objects.filter(status='Signed').count(),
        'expired_contracts': Contract.objects.filter(status='Expired').count(),
        'recent_contracts': Contract.objects.all().order_by('-created_date')[:10]
    }
    return render(request, 'contract_intro.html', context)

@login_required
def create_contract(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.admin = request.user  # Set the admin to the current user
            
            # Fetch the user's farm dimensions (assuming you have a Farm model)
            farm = request.user.farms.first()  # Get the first farm associated with the user
            if farm:
                # Set chick capacity based on farm dimensions
                contract.chick_capacity = farm.coopcapacity  # Assuming coopcapacity is the max number of chicks
                
            contract.save()
            return redirect('contract_detail', contract_id=contract.id)  # Redirect to contract detail page
    else:
        form = ContractForm()
    return render(request, 'create_contract.html', {'form': form})

@login_required
def view_contracts(request):
    contracts = Contract.objects.all()
    if not request.user.is_superuser:  # If not admin, only show contracts related to the user
        contracts = contracts.filter(
            models.Q(admin=request.user) | models.Q(stakeholder=request.user))
    
    context = {
        'contracts': contracts
    }
    return render(request, 'view_contracts.html', context)

@login_required
def get_farm_details(request):
    if request.method == 'GET':
        stakeholder_id = request.GET.get('stakeholder_id')
        farms = Farm.objects.filter(owner_id=stakeholder_id).values('name', 'length', 'breadth', 'coopcapacity')
        
        if farms.exists():
            farm_details = list(farms)
            return JsonResponse({'success': True, 'farms': farm_details})
        else:
            return JsonResponse({'success': False, 'message': 'No farms found for this stakeholder.'})

@login_required
def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    context = {
        'contract': contract
    }
    return render(request, 'contract_detail.html', context)

#   from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa

@login_required
def generate_contract_pdf(request, contract_id):
       contract = get_object_or_404(Contract, id=contract_id)
       html_string = render_to_string('contract_detail.html', {'contract': contract})
       response = HttpResponse(content_type='application/pdf')
       response['Content-Disposition'] = f'attachment; filename="contract_{contract_id}.pdf"'
       pisa_status = pisa.CreatePDF(html_string, dest=response)
       if pisa_status.err:
           return HttpResponse('Error generating PDF', status=500)
       return response
   
   
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .models import Contract

@login_required
def sign_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        signature = data.get('signature')
        
        if not signature:
            return JsonResponse({'success': False, 'message': 'No signature provided'})
            
        if request.user == contract.admin and contract.status == 'Pending_Admin':
            contract.admin_signature = signature
            contract.admin_signed_date = timezone.now()
            contract.status = 'Pending_Stakeholder'
            contract.save()
            return JsonResponse({'success': True})
            
        elif request.user == contract.stakeholder and contract.status == 'Pending_Stakeholder':
            contract.stakeholder_signature = signature
            contract.stakeholder_signed_date = timezone.now()
            contract.status = 'Active'
            contract.save()
            return JsonResponse({'success': True})
            
        return JsonResponse({'success': False, 'message': 'Invalid signing attempt'})
        
    return render(request, 'contract_detail.html', {'contract': contract})


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from user.models import ChatRoom, ChatMessage, User
from django.http import JsonResponse
from django.db.models import Q

@login_required
def admin_chat_view(request):
    # Get all stakeholders with their chat rooms
    stakeholders = User.objects.filter(
        user_type__name='Stakeholder'
    ).prefetch_related('chat_rooms')
    
    # Create chat rooms for stakeholders who don't have one
    for stakeholder in stakeholders:
        if not stakeholder.chat_rooms.exists():
            ChatRoom.objects.create(
                stakeholder=stakeholder,
                farm_name=f"{stakeholder.full_name}'s Farm"
            )
    
    context = {
        'stakeholders': stakeholders,
    }
    
    return render(request, 'admin_chat.html', context)

@login_required
def stakeholder_chat_view(request):
    # Get or create chat room for this stakeholder
    chat_room, created = ChatRoom.objects.get_or_create(
        stakeholder=request.user,
        defaults={'farm_name': f"{request.user.full_name}'s Farm"}
    )
    
    # Get all admin users
    admins = User.objects.filter(is_staff=True)
    
    # Handle message sending
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(
                room=chat_room,
                sender=request.user,
                message=message_text
            )
            return redirect('stakeholder_chat_view')
    
    # Get all messages for this room
    chat_messages = ChatMessage.objects.filter(room=chat_room).order_by('created_at')
    
    return render(request, 'stakeholder_chat.html', {
        'chat_room': chat_room,
        'messages': chat_messages,
        'admins': admins  # Add this to the context
    })

@login_required
def get_chat_messages(request, room_id):
    try:
        # Get specific chat room
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        # Get messages only for this specific room
        messages = ChatMessage.objects.filter(room=chat_room).order_by('created_at')
        
        messages_data = [{
            'text': msg.message,
            'sender': msg.sender.full_name,
            'sender_type': 'admin' if msg.sender.is_staff else 'stakeholder',
            'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for msg in messages]
        
        return JsonResponse({
            'status': 'success',
            'messages': messages_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def get_unread_message_count(request):
    """
    Get count of unread messages for the current user
    """
    try:
        if request.user.is_staff:
            # For admin, count unread messages from all chat rooms
            unread_count = ChatMessage.objects.filter(
                is_read=False
            ).exclude(
                sender=request.user
            ).count()
        else:
            # For stakeholder, count unread messages in their chat room
            unread_count = ChatMessage.objects.filter(
                room__stakeholder=request.user,
                is_read=False
            ).exclude(
                sender=request.user
            ).count()

        return JsonResponse({
            'status': 'success',
            'unread_count': unread_count
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def mark_messages_read(request, room_id):
    """
    Mark all messages in a room as read
    """
    try:
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # Check if user has access to this chat room
        if not (request.user.is_staff or request.user == chat_room.stakeholder):
            return JsonResponse({
                'status': 'error',
                'message': 'Access denied'
            }, status=403)

        # Mark all messages as read
        ChatMessage.objects.filter(
            room=chat_room
        ).exclude(
            sender=request.user
        ).update(is_read=True)

        return JsonResponse({
            'status': 'success',
            'message': 'Messages marked as read'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@ensure_csrf_cookie
def send_message(request, room_id):
    if request.method == 'POST':
        try:
            # Get specific chat room
            chat_room = get_object_or_404(ChatRoom, id=room_id)
            message_text = request.POST.get('message')
            
            if not message_text:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Message content is required'
                }, status=400)

            # Create message in specific room
            message = ChatMessage.objects.create(
                room=chat_room,
                sender=request.user,
                message=message_text
            )
            
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'text': message.message,
                    'sender': message.sender.full_name,
                    'sender_type': 'admin' if message.sender.is_staff else 'stakeholder',
                    'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

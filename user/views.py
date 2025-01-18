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
from django.db.models import Sum, Count

from stakeholder.models import ChickBatch, DailyData,ChickSupply
from .forms import EmailAuthenticationForm
from .forms import CustomUserCreationForm, EmailAuthenticationForm, StakeholderUserForm
from .models import UserType, User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import pandas as pd
from math import floor
import openpyxl
from .models import WasteManagementResource, DailyTip


def register(request):
    user_type_param = request.GET.get('user_type')
    print(user_type_param)
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

        elif user.expiry_date and user.expiry_date < date.today():
            # Redirect the user to an 'expiry notification' page if the certificate has expired
            return reverse_lazy('expiry_notification')

        elif user.user_type != None and user.user_type.name.lower() == 'admin':
            return reverse_lazy('admindash')
        elif user.user_type != None and user.user_type.name.lower() == 'customer':
            return reverse_lazy('hoteldashboard')
        return self.success_url


def admindash(request):
    completed_orders_count = 0
    completed_batches_sales_count = 0
    # Fetching the usertype with name 'Stakeholder'
    stakeholder_user_type = UserType.objects.get(name='Stakeholder')

    # Counting total stakeholders
    total_stakeholders = User.objects.filter(
        user_type=stakeholder_user_type).count()

    # Counting active stakeholders
    active_stakeholders = User.objects.filter(
        user_type=stakeholder_user_type, is_active=True).count()

    # Fetching the usertype with name 'Customer'
    customer_user_type = UserType.objects.get(name='Customer')
    customer_count = User.objects.filter(user_type=customer_user_type).count()

    completed_orders_count = Order.objects.filter(status='completed').count()
    pending_orders = Order.objects.filter(status='pending').order_by('-order_date')[:3]
    completed_batches_sales_count = ChickBatch.objects.filter(batch_status='completed') \
    .annotate(order_count=Count('order')) \
    .aggregate(total_sales=Sum('order_count'))['total_sales'] or 0
    chicken_type_totals = ChickBatch.objects.values('batch_type').annotate(
        total_one_kg=Sum('one_kg_count'),
        total_two_kg=Sum('two_kg_count'),
        total_three_kg=Sum('three_kg_count')
    )

    # Counting total farms (assuming stakeholders are farms)
    total_farm = total_stakeholders
    farmactive_count = active_stakeholders
    
    # Aggregating total chicks supplied by type
    chicks_supplied_by_type = ChickSupply.objects.values('chicken_type').annotate(total_supplied=Sum('chicks_supplied'))
    print(list(chicks_supplied_by_type))

    return render(request, 'dashboard.html', {
        'stakeholder_count': total_stakeholders,
        'customer_count': customer_count,
        'farmactive_count': farmactive_count,
        'total_farm': total_farm,
        'completed_orders_count': completed_orders_count,
        'pending_orders': pending_orders,
        'completed_batches_sales_count': completed_batches_sales_count,
        'chicken_type_totals': chicken_type_totals,
        'chicks_supplied_by_type': chicks_supplied_by_type
    })

def stakeholderuser(request):
    # fetching the usertype with name stakeholder
    user_type = UserType.objects.get(name='Stakeholder')
    users = User.objects.filter(user_type=user_type)
    context = {'users': users}
    return render(request, 'stakeholderuser.html', context)


def stakeholderuserprofile(request, id):
    user = User.objects.get(id=id)
    chick_batches = ChickBatch.objects.filter(user=user)
    total_chick_count = chick_batches.aggregate(Sum('initial_chick_count'))[
        'initial_chick_count__sum'] or 0

    today = date.today()
    day_expiry = None
    if user.expiry_date:
        day_expiry = (user.expiry_date - today).days

    # Calculate square feet based on length and breadth (assuming they're in the User model)
    sqr_feet = 0
    if user.length and user.breadth:
        sqr_feet = user.length * user.breadth
    sqr_feet_rounded = round(sqr_feet, 0)

    # Calculate number of birds that can be accommodated
    birds_per_square_feet = 2
    birds_can_accommodate = floor(
        sqr_feet * birds_per_square_feet)  # Use floor to round down

    if request.method == 'POST':

        if not user.is_active:
            messages.error(
                request, "You cannot add chicks because the user account is disabled.")
            return redirect('stakeholderuserprofile', id=id)

        initial_chick_count = request.POST.get('initial_chick_count')
        batch_size = request.POST.get('batch_size')
        price_per_kg = request.POST.get('price_per_kg')
        price_per_batch = request.POST.get('price_per_batch')

        # Backend validation: Chick count must not be less than zero
        try:
            # Ensure integer conversion
            initial_chick_count = int(initial_chick_count)
            if initial_chick_count < 0:
                messages.error(
                    request, "Chick count cannot be less than zero.")
                return redirect('stakeholderuserprofile', id=id)
        except (ValueError, TypeError):
            # Catch any errors where the input cannot be converted to an integer
            messages.error(
                request, "Invalid chick count entered. Please enter a valid number.")
            return redirect('stakeholderuserprofile', id=id)
        # Check if the new chick count exceeds capacity

        # Save the chick count to the user's chick batches or user model (depending on your logic)
        # Assuming you want to update chick batches:
        ChickBatch.objects.create(
            user=user, initial_chick_count=initial_chick_count, batch_size=batch_size, price_per_kg=price_per_kg, price_per_batch=price_per_batch)
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


from django.shortcuts import render, redirect, get_object_or_404
from .forms import StakeholderUserForm
from .models import User

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import StakeholderUserForm  # Ensure you import the correct form
from .models import User  # Ensure you import the User model correctly

def stakeholder_registration(request, id):
    # Fetch the user by ID
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        # Bind form with POST data and FILES for image/file uploads
        user_form = StakeholderUserForm(request.POST, request.FILES, instance=user)
        
        if user_form.is_valid():
            # Save the form data (including file uploads)
            user_form.save()

            # Add a success message
            messages.success(request, 'Profile updated successfully.')

            # Redirect to the stakeholder page or success page
            return redirect('stakeholder')  # Ensure 'stakeholder' is defined in urls.py
        else:
            # Add an error message for invalid form data
            messages.error(request, 'There was an error updating the profile. Please check the form and try again.')

            # Render the form with errors
            return render(request, 'stakeholder_profile.html', {'user_form': user_form})
    else:
        # Prepopulate the form with the user's current data
        user_form = StakeholderUserForm(instance=user)

    # Render the form template
    return render(request, 'stakeholder_profile.html', {'user_form': user_form})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User

import json
from django.http import JsonResponse
from .utils import get_address_from_coordinates
from django.contrib.auth.models import User

def update_location(request):
    """
    Updates the user's location and address based on latitude and longitude.
    """
    if request.method == 'POST':
        try:
            # Parse JSON data from request
            data = json.loads(request.body)
            user_id = data.get('user_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            # Validate the presence of latitude and longitude
            if not (latitude and longitude):
                return JsonResponse({'success': False, 'message': 'Latitude and longitude are required.'}, status=400)

            # Fetch the user
            user = User.objects.filter(id=user_id).first()
            if not user:
                return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

            # Get address details using coordinates
            address_details = get_address_from_coordinates(float(latitude), float(longitude))
            if 'error' in address_details:
                return JsonResponse({'success': False, 'message': 'Failed to fetch address from coordinates.'}, status=500)

            # Update the user profile
            user_profile = user.profile  # Assuming a one-to-one relationship with a Profile model
            user_profile.location = f"{latitude}, {longitude}"
            user_profile.address = f"{address_details.get('road', '')}, {address_details.get('suburb', '')}, {address_details.get('city', '')}, {address_details.get('state', '')}, {address_details.get('country', '')}"
            user_profile.region = address_details.get('region', 'Unknown')
            user_profile.save()

            return JsonResponse({'success': True, 'message': 'Location and address updated successfully.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


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

def manage_vaccines(request):

    return render(request, 'manage_vaccines.html')

# View to add a new vaccine
from django.http import JsonResponse
from django.shortcuts import render
from .forms import VaccineForm

def add_vaccine(request):
    if request.method == 'POST':
        form = VaccineForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Vaccine added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Form is invalid', 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# View to edit an existing vaccine
def edit_vaccine(request, vaccine_id):
    vaccine = get_object_or_404(Vaccine, id=vaccine_id)
    if request.method == 'POST':
        form = VaccineForm(request.POST, instance=vaccine)
        if form.is_valid():
            form.save()
            messages.success(request, "Vaccine updated successfully!")
            return redirect('vaccine_dashboard')
    else:
        form = VaccineForm(instance=vaccine)
    return render(request, 'edit_vaccine.html', {'form': form})

def delete_vaccine(request, vaccine_id):
    # Get the vaccine object by ID
    vaccine = get_object_or_404(Vaccine, id=vaccine_id)

    # Delete the vaccine
    vaccine.delete()

    # Return a JSON response indicating success
    return JsonResponse({'success': True, 'message': 'Vaccine deleted successfully'})


def vaccine_dashboard(request):
    vaccines = Vaccine.objects.all()
    return render(request, 'vaccine_dashboard.html', {'vaccines': vaccines})





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
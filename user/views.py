from datetime import date
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Sum

from stakeholder.models import ChickBatch
from .forms import EmailAuthenticationForm
from .forms import CustomUserCreationForm, EmailAuthenticationForm, StakeholderUserForm
from .models import UserType, User
from django.shortcuts import get_object_or_404
import math
from math import floor  



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
        
        if user.expiry_date and user.expiry_date < date.today():
            # Redirect the user to an 'expiry notification' page if the certificate has expired
            return reverse_lazy('expiry_notification') 

        elif user.user_type != None and user.user_type.name.lower() == 'admin':
            return reverse_lazy('admindash')
        return self.success_url


def admindash(request):
    # Fetching the usertype with name 'Stakeholder'
    stakeholder_user_type = UserType.objects.get(name='Stakeholder')
    
    # Counting total stakeholders
    total_stakeholders = User.objects.filter(user_type=stakeholder_user_type).count()

    # Counting active stakeholders
    active_stakeholders = User.objects.filter(user_type=stakeholder_user_type, is_active=True).count()

    # Fetching the usertype with name 'Customer'
    customer_user_type = UserType.objects.get(name='Customer')
    customer_count = User.objects.filter(user_type=customer_user_type).count()
    
    # Counting total farms
    total_farm = total_stakeholders  # Assuming User model represents farms (in this case, stakeholders are farms)
    
    # Counting active farms (which are essentially active stakeholders)
    farmactive_count = active_stakeholders

    return render(request, 'dashboard.html', {
        'stakeholder_count': total_stakeholders,
        'customer_count': customer_count,
        'farmactive_count': farmactive_count,
        'total_farm': total_farm
    })



def stakeholderuser(request):
    # fetching the usertype with name stakeholder
    user_type = UserType.objects.get(name='Stakeholder')
    users = User.objects.filter(user_type=user_type)
    context = {'users': users}
    return render(request, 'stakeholderuser.html', context)


from django.db.models import Sum
from datetime import date

def stakeholderuserprofile(request, id):  
    user = User.objects.get(id=id)
    chick_batches = ChickBatch.objects.filter(user=user)
    total_chick_count = chick_batches.aggregate(Sum('initial_chick_count'))['initial_chick_count__sum'] or 0
    
    

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
    birds_per_square_feet =2
    birds_can_accommodate = floor(sqr_feet * birds_per_square_feet)  # Use floor to round down
    
    if request.method == 'POST':
        
        if not user.is_active:
            messages.error(request, "You cannot add chicks because the user account is disabled.")
            return redirect('stakeholderuserprofile', id=id)

        initial_chick_count = request.POST.get('initial_chick_count')
        
        
        # Backend validation: Chick count must not be less than zero
        try:
            initial_chick_count = int(initial_chick_count)  # Ensure integer conversion
            if initial_chick_count < 0:
                messages.error(request, "Chick count cannot be less than zero.")
                return redirect('stakeholderuserprofile', id=id)
        except (ValueError, TypeError):
            # Catch any errors where the input cannot be converted to an integer
            messages.error(request, "Invalid chick count entered. Please enter a valid number.")
            return redirect('stakeholderuserprofile', id=id)
        # Check if the new chick count exceeds capacity
        

        # Save the chick count to the user's chick batches or user model (depending on your logic)
        # Assuming you want to update chick batches:
        ChickBatch.objects.create(user=user, initial_chick_count=initial_chick_count)
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
    sqr_feet = 0
    return render(request, 'customerprofile.html', {'user': user})


def stakeholder_registration(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        form = StakeholderUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()  # Save the updated user profile
            
            # Redirect to a success page or wherever you need
            return redirect('stakeholder')
    else:
        form = StakeholderUserForm(instance=user)

    return render(request, 'stakeholder_profile.html', {'form': form})


def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        # Toggle the user's active status
        user.is_active = not user.is_active
        user.save()
        
        status = "enabled" if user.is_active else "disabled"
        messages.success(request, f"User has been {status} successfully.")
    
    return redirect('stakeholderuser') 

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()  # Delete the user
    return redirect('stakeholderuser')


def vaccine_admin(request):
    # Assuming you're trying to retrieve a VaccineAdmin object by its ID (pk)

    return render(request, 'vaccination.html')

def feed_admin(request):
    return render(request, 'feedadmin.html')


# user/views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import User

def renew_pollution_certificate(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_expiry_date = request.POST.get('expiry_date')
        if new_expiry_date:
            user.expiry_date = new_expiry_date  # Update the expiry date
            user.is_active = True  # Reactivate the user
            user.save()
            messages.success(request, "Pollution certificate renewed successfully.")
        else:
            messages.error(request, "Please provide a valid expiry date.")
    
    return redirect('stakeholder')  # Replace 'some_view' with the appropriate view name

# user/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier
from .forms import SupplierForm

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
            messages.success(request, 'Supplier added successfully.')  # Success message
            return redirect('supplier_list')  # Redirect to supplier list after adding
        else:
            # This part will execute if the form is not valid
            messages.error(request, 'Please correct the errors below.')  # Error message
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
            return redirect('supplier_list')  # Redirect to supplier list after editing
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'edit_supplier.html', {'form':form})

def enable_supplier(request, supplier_id):
    """Enable a supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.is_active = True
    supplier.save()
    return redirect('supplier_list')  # Redirect to supplier list after enabling

def disable_supplier(request, supplier_id):
    """Disable a supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.is_active = False
    supplier.save()
    return redirect('supplier_list')  # Redirect to supplier list after disabling


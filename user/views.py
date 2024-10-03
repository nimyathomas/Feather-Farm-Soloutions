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

        elif user.user_type != None and user.user_type.name.lower() == 'admin':
            return reverse_lazy('admindash')
        return self.success_url


def admindash(request):
    # fetching the usertype with name stakeholder
    user_type = UserType.objects.get(name='Stakeholder')
    stakeholder_count = User.objects.filter(user_type=user_type)

    # fetching the usertype with name stakeholder
    user_type = UserType.objects.get(name='Customer')
    customer_count = User.objects.filter(user_type=user_type)

    return render(request, 'dashboard.html', {'stakeholder_count': stakeholder_count.count(), 'customer_count': customer_count.count()})


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
    total_chick_count = chick_batches.aggregate(Sum('chick_count'))['chick_count__sum'] or 0

    today = date.today()
    day_expiry = None
    if user.expiry_date:
        day_expiry = (user.expiry_date - today).days
    
    # Calculate square feet based on length and breadth (assuming they're in the User model)
    sqr_feet = 0  
    if user.length and user.breadth:
        sqr_feet = user.length * user.breadth
    
    # Calculate number of birds that can be accommodated
    birds_can_accommodate = sqr_feet * 4  # 4 birds per sq foot
    
    context = {
        'user': user,
        'total_chick_count': total_chick_count,
        'day_expiry': day_expiry,
        'sqr_feet': sqr_feet,
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


def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()  # Delete the user
    return redirect('stakeholderuser')


def vaccine_admin(request):
    # Assuming you're trying to retrieve a VaccineAdmin object by its ID (pk)

    return render(request, 'vaccination.html')

def feed_admin(request):
    return render(request, 'feedadmin.html')
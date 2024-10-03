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

@login_required
def stakeholder(request):
    user = request.user  # Assuming the user is logged in
    today = timezone.now().date()
    # Fetch all chick batches for the user and order them by the latest batch_date
    chick_batches = user.chick_batches.all().order_by('-batch_date')

    # Calculate the total chick count across all batches
    total_chick_count = sum(batch.chick_count for batch in chick_batches)

    coming_soon = [batch for batch in chick_batches if 0 <=
                   (batch.batch_date - today).days <= 7]
    upcoming = [batch for batch in chick_batches if 7 < (batch.batch_date - today).days <= 40 and batch.batch_date >= today]
    # Calculate dates for alert (3 days before upcoming batch date)
    alert_vaccine_dates = [(batch.batch_date - timedelta(days=3)) for batch in upcoming if 7 < (batch.batch_date - today).days <= 40]
    coming_soon_dates = [
        (batch.batch_date + timedelta(days=7))
        for batch in chick_batches
        if 0 <= (batch.batch_date - today).days <= 7
    ]
    upcoming_dates = [(batch, batch.batch_date + timedelta(days=40)) for batch in upcoming]
    sqr_feet = 0
    if user.length and user.breadth:
      sqr_feet = user.length * user.breadth
      coop_capacity=sqr_feet*4
    context = {
        'chick_batches': chick_batches,
        'coming_soon': coming_soon,
        'upcoming': upcoming,
        'total_chick_count': total_chick_count,  # Total chick count
        'sqr_feet':sqr_feet,
        'coming_soon_dates': coming_soon_dates,
        'upcoming_dates': upcoming_dates,        # Upcoming dates with batch_date + 40
        'alert_vaccine_dates': alert_vaccine_dates,
        'today': today,  # Pass today's date to the template
        'user_data': user,
        
    }
    return render(request, 'stakeholderdash.html', context)


def stateholder_batch(request):
    user = request.user  # Assuming the user is logged in
    chick_batches = user.chick_batches.all().order_by('-batch_date')

    total_chick_count = sum(batch.chick_count for batch in chick_batches)
    context = {
        'chick_batches': chick_batches,
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
            return HttpResponse("No users there.")
        
        # Get chick count from the form
        chick_count = request.POST.get('chick_count')
        
        try:
            chick_count = int(chick_count)  # Convert to integer
        except ValueError:
            messages.error(request, "Invalid chick count value.")
            return redirect(reverse('stakeholderuserprofile', args=[id]))
        
        # Calculate the coop capacity based on the user's length and breadth
        if user.length and user.breadth:
            sqr_feet = user.length * user.breadth
            coop_capacity = sqr_feet * 4  # 4 birds per sq ft
        else:
            messages.error(request, "Please ensure that the coop's length and breadth are provided.")
            return redirect(reverse('stakeholderuserprofile', args=[id]))

        # Validate that the entered chick count does not exceed the coop capacity
        if chick_count <= coop_capacity:
            # Create a new ChickBatch record for the current user
            ChickBatch.objects.create(
                user=user,
                chick_count=chick_count,
                batch_date=timezone.now()  # Automatically set to the current date
            )
            messages.success(request, "Chick batch successfully added.")
            return redirect('stakeholderuser')
        else:
            messages.error(request, f"You can't add more than {coop_capacity} birds for the current coop size.")
            return redirect(reverse('stakeholderuserprofile', args=[id]))

    return redirect('stakeholderuserprofile')

def feed_request(request, user_id):
    user=get_object_or_404(User, id=user_id)
    return render(request, 'feed_request.html') 


def vaccination(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'vaccinations.html', {'user': user})

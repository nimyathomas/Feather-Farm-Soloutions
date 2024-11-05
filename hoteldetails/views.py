from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Q  # Import Q for complex queries
from django.urls import reverse
from hoteldetails.models import Order,Cart,CartItem
from stakeholder.models import ChickBatch
from user.models import UserType, User
from .forms import CustomerUserForm, OrderForm
from django.contrib import messages
from decimal import Decimal



def hoteldashboard(request):
    # fetching the search data from html search box
    # fetching the search data from html search box
    query = request.GET.get('q')
    batch_type = request.GET.get('batch_type')
    user_type = UserType.objects.get(name='Stakeholder')
    users = User.objects.filter(user_type=user_type)
    if query:
        # Filter items based on title or description matching the query
        users = users.filter(
            Q(name_icontains=query) | Q(chick_batches_batch_type=query)
        )
    if batch_type:
        users = users.filter(
            chick_batches__batch_type=batch_type
        )
    paginator = Paginator(users, 6)
    # Get the page number from the query parameter
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'hoteldetials/farmlist.html', {'page_obj': page_obj})


def view_profile(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = CustomerUserForm(request.POST, instance=user)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect('hoteldashboard')
    else:
        form = CustomerUserForm(instance=user)
    return render(request, 'hoteldetials/view_profile.html', {"form": form})


from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ValidationError

def view_farm(request, farm_id):
    farm = get_object_or_404(User, id=farm_id)
    batches = farm.chick_batches.filter(
        batch_status='completed')  # Only show completed batches
    order_form = OrderForm()

    if request.method == 'POST':
        form = OrderForm(request.POST)
        batch_id = request.POST.get('batch_id')
        batch = get_object_or_404(ChickBatch, id=batch_id)

        if form.is_valid():
            # Extract quantities from the form
            one_kg_count = form.cleaned_data['one_kg_count'] or 0
            two_kg_count = form.cleaned_data['two_kg_count'] or 0
            three_kg_count = form.cleaned_data['three_kg_count'] or 0

            # Custom validation: Check if at least one of the quantities is filled
            if one_kg_count == 0 and two_kg_count == 0 and three_kg_count == 0:
               
                messages.error(request, "Please fill in at least one of the quantities.")
                
            else:
                # Ensure order does not exceed available stock
                if (one_kg_count <= batch.one_kg_count and
                    two_kg_count <= batch.two_kg_count and
                        three_kg_count <= batch.three_kg_count):
                    # Get or create the user's cart
                    cart, created = Cart.objects.get_or_create(user=request.user)

                    # Create a new CartItem or update if it exists for the same batch
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, chick_batch=batch)
                    cart_item.one_kg_count += one_kg_count
                    cart_item.two_kg_count += two_kg_count
                    cart_item.three_kg_count += three_kg_count
                    cart_item.save()

                    # Redirect to cart page or display a success message
                    return redirect('cart_view')
                else:
                    form.add_error(
                        None, "The requested quantities exceed available stock.")

    return render(request, 'hoteldetials/view_farms.html', {
        'farm': farm,
        'batches': batches,
        'order_form': order_form,
    })



def cart_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = None
    cartitems = CartItem.objects.filter(cart=cart)
    total_price = sum(item.total_price() for item in cartitems)
    total_discounted = sum(item.discounted_price for item in cartitems)
    is_empty = len(cartitems) == 0
    return render(request, 'hoteldetials/view_cart.html', {"cart": cart, "items": cartitems, "total_price": total_price, "total_dicounted_price": total_discounted,"is_empty": is_empty })


def update_cart(request):
    if request.method == 'POST':
        # Get the current user's cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            # Handle case if no cart exists
            return redirect('cart_view')

        # Update each item based on form data
        for item in cart.items.all():
            # Update the type (live or processed)
            item_type = request.POST.get(f'type_{item.id}')
            if item_type == 'processed':
                item.is_processed = True
                item.save()

        cart.save()
        # Redirect to a checkout page or back to the cart with updated information
        return redirect('checkout_view')

    # If GET request, redirect back to the cart view
    return redirect('cart_view')


def checkout_view(request):
    cart = Cart.objects.get(user=request.user)  # Get user's cart
    items = cart.items.all()
    
    # Check if the cart has items
    if not items:
        # Redirect or display a message if the cart is empty
        return redirect('cart_view')  # Or display an error message

    # Calculate the base total price
    total_price = sum(item.discounted_price for item in items)

    if request.method == "POST":
        # Handle delivery date, payment method, and delivery option
        delivery_date = request.POST.get('delivery_date')
        payment_method = request.POST.get('payment_option')
        delivery_option = request.POST.get('delivery_method')  # Retrieve selected delivery option
        
        # Adjust the total price based on the delivery option
        if delivery_option == 'express':
            total_price += Decimal('500.00')  # Add express delivery fee
        elif delivery_option == 'standard':
            total_price += Decimal('0.00')  # No extra charge for standard delivery

        # Create the order
        order = Order.objects.create(
            user=request.user,
            batch=items[0].chick_batch,  # Assume all items belong to the same batch
            one_kg_count=sum(item.one_kg_count for item in items),
            two_kg_count=sum(item.two_kg_count for item in items),
            three_kg_count=sum(item.three_kg_count for item in items),
            payment_method=payment_method if payment_method in ['cod', 'online', 'upi'] else 'cod',
            price=total_price, 
            delivery_option=delivery_option,
            delivery_date=delivery_date if delivery_date else None,
            status='pending',
        )

        # Optionally, clear the cart after placing the order
        cart.items.all().delete()  # Clear the cart items
        cart.save()
        return redirect('view_orders')

    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price,
    }
    return render(request, 'hoteldetials/checkout_view.html', context)


def view_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'hoteldetials/orderview.html', {'orders': orders})

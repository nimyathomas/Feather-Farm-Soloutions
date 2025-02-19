from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Q  # Import Q for complex queries
from hoteldetails.models import Order, Cart, CartItem, HotelUser
from stakeholder.models import ChickBatch
from user.models import User
from stakeholder.models import Farm
from .forms import HotelFormUserForm, HotelForm, OrderForm
from django.contrib import messages
from decimal import Decimal
from .utility import calculate_distance
from datetime import datetime, timedelta
from django.contrib import messages
from django.http import JsonResponse
from .utility import send_order_confirmation_email
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import decimal
from .models import WalletTransaction  # Replace Transaction with WalletTransaction
import razorpay
from django.views.decorators.csrf import csrf_exempt
import json

def hoteldashboard(request):
    batch_type = request.GET.get("batch_type", "")
    query = request.GET.get("q", "")
    max_distance = request.GET.get("max_distance", None)

    # Get user coordinates
    hoteluser = HotelUser.objects.filter(hotel_owner=request.user).first()
    user_lat = request.GET.get("latitude") or (hoteluser.latitude if hoteluser else None)
    user_lon = request.GET.get("longitude") or (hoteluser.longitude if hoteluser else None)

    if not user_lat or not user_lon:
        messages.warning(request, "Please update your location in profile settings.")
        return redirect('view_profile', id=request.user.id)

    try:
        user_lat = float(user_lat)
        user_lon = float(user_lon)
    except (ValueError, TypeError):
        messages.error(request, "Invalid location coordinates.")
        return redirect('view_profile', id=request.user.id)

    # Debug print
    print(f"User coordinates: {user_lat}, {user_lon}")

    # Add more detailed debug for completed batches
    completed_batches = ChickBatch.objects.filter(batch_status='completed')
    print(f"\nDetailed batch information:")
    for batch in completed_batches:
        print(f"""
        Batch ID: {batch.id}
        Farm: {batch.farm.name}
        Status: {batch.batch_status}
        Type: {batch.batch_type}
        Weight Distribution:
        - 1 KG: {batch.one_kg_count}
        - 2 KG: {batch.two_kg_count}
        - 3 KG: {batch.three_kg_count}
        Price per KG: {batch.price_per_kg}
        """)

    # Get farms with completed batches
    farms = Farm.objects.filter(
        chick_batches__batch_status='completed'
    ).distinct()
    
    print(f"Total farms with completed batches: {farms.count()}")

    # Apply filters
    if batch_type:
        farms = farms.filter(chick_batches__batch_type=batch_type)
    if query:
        farms = farms.filter(name__icontains=query)

    recommended_farms = []
    for farm in farms:
        print(f"\nProcessing farm: {farm.name}")
        print(f"Farm coordinates: {farm.latitude}, {farm.longitude}")
        
        # Validate farm coordinates
        if (farm.latitude and farm.longitude and 
            -90 <= farm.latitude <= 90 and 
            -180 <= farm.longitude <= 180):
            
            distance = calculate_distance(
                (user_lat, user_lon),
                (farm.latitude, farm.longitude)
            )
            farm.distance = round(distance, 2)
            print(f"Distance to farm: {farm.distance} km")

            # Add farm if within distance limit
            if max_distance:
                if distance <= float(max_distance):
                    recommended_farms.append(farm)
                    print(f"Added farm (within max distance)")
            elif distance <= 50:  # Default 50km radius
                recommended_farms.append(farm)
                print(f"Added farm (within default radius)")
        else:
            print(f"Invalid coordinates for farm: {farm.name}")
            # Still add the farm but with a default distance
            farm.distance = 0
            recommended_farms.append(farm)

    print(f"\nTotal recommended farms: {len(recommended_farms)}")

    # Sort by distance
    recommended_farms.sort(key=lambda x: x.distance)

    # Add completed batches to each farm for template access
    for farm in recommended_farms:
        completed_batches = farm.chick_batches.filter(batch_status='completed')
        farm.completed_batches = completed_batches
        print(f"Farm {farm.name} has {completed_batches.count()} completed batches")

    # Pagination
    paginator = Paginator(recommended_farms, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "hotel_name": hoteluser.hotel_name if hoteluser else "",
        "batch_type": batch_type,
        "total_farms": len(recommended_farms)
    }

    return render(request, "hoteldetials/farmlist.html", context)


def view_profile(request, id):
    user = get_object_or_404(User, id=id)
    hotel = HotelUser.objects.filter(hotel_owner=user).first() or HotelUser(
        hotel_owner=user
    )
    hotel_form = HotelForm(instance=hotel)
    user_form = HotelFormUserForm(instance=user)
    print(request.POST)
    if request.method == "POST":
        if "update_profile" in request.POST:
            # Handle Profile Update
            user_form = HotelFormUserForm(request.POST, instance=user)

            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("hoteldashboard")
            else:
                messages.error(
                    request, "Error updating the profile. Check the form and try again."
                )
        elif "update_hotel" in request.POST:  # Handle Farm Details Update
            hotel_form = HotelForm(request.POST, request.FILES, instance=hotel)
            print(hotel_form.errors)
            if hotel_form.is_valid():
                hotel_form.save()
                return redirect("hoteldashboard")
    return render(
        request,
        "hoteldetials/view_profile.html",
        {"hotel_form": hotel_form, "user_form": user_form},
    )


def view_farm(request, farm_id):
    user = get_object_or_404(User, id=request.user.id)
    farm = Farm.objects.get(id=farm_id)
    batches = farm.chick_batches.filter(
        batch_status="completed"
    )  # Only show completed batches
    order_form = OrderForm()

    if request.method == "POST":
        form = OrderForm(request.POST)
        batch_id = request.POST.get("batch_id")
        batch = get_object_or_404(ChickBatch, id=batch_id)

        if form.is_valid():
            # Extract quantities from the form
            one_kg_count = form.cleaned_data["one_kg_count"] or 0
            two_kg_count = form.cleaned_data["two_kg_count"] or 0
            three_kg_count = form.cleaned_data["three_kg_count"] or 0

            # Custom validation: Check if at least one of the quantities is filled
            if one_kg_count == 0 and two_kg_count == 0 and three_kg_count == 0:

                messages.error(
                    request, "Please fill in at least one of the quantities."
                )

            else:
                # Ensure order does not exceed available stock
                if (
                    one_kg_count <= batch.one_kg_count
                    and two_kg_count <= batch.two_kg_count
                    and three_kg_count <= batch.three_kg_count
                ):
                    # Get or create the user's cart
                    cart, created = Cart.objects.get_or_create(user=request.user)

                    # Create a new CartItem or update if it exists for the same batch
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, chick_batch=batch
                    )
                    cart_item.one_kg_count += one_kg_count
                    cart_item.two_kg_count += two_kg_count
                    cart_item.three_kg_count += three_kg_count
                    cart_item.save()

                    # Redirect to cart page or display a success message
                    return redirect("cart_view")
                else:
                    form.add_error(
                        None, "The requested quantities exceed available stock."
                    )

    return render(
        request,
        "hoteldetials/view_farms.html",
        {
            "farm": farm,
            "user": user,
            "batches": batches,
            "order_form": order_form,
        },
    )


def cart_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = None
    cartitems = CartItem.objects.filter(cart=cart)
    total_price = sum(item.total_price() or 0 for item in cartitems)
    total_discounted = sum(item.discounted_price for item in cartitems)
    is_empty = len(cartitems) == 0
    return render(
        request,
        "hoteldetials/view_cart.html",
        {
            "cart": cart,
            "items": cartitems,
            "total_price": total_price,
            "total_dicounted_price": total_discounted,
            "is_empty": is_empty,
        },
    )


def update_cart(request):
    if request.method == "POST":
        # Retrieve the cart
        cart = get_object_or_404(Cart, user=request.user)
        # Iterate through the submitted items and update their types
        for item_id, item_type in request.POST.items():
            if item_id.startswith("type_"):  # Check for type-related keys
                cart_item_id = item_id.split("_")[1]
                cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
                cart_item.is_processed = item_type == "processed"
                cart_item.item_type = item_type
                cart_item.save()
                print(cart_item.is_processed)

        # Recalculate totals
        cartitems = CartItem.objects.filter(cart=cart)
        return redirect('checkout_view')

    return JsonResponse({"error": "Invalid request method"}, status=400)


def checkout_view(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.items.all()

    # Check if the cart has items
    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart_view")

    # Calculate prices
    total_price = sum(item.total_price() or Decimal("0.00") for item in items)
    total_discounted = sum(item.discounted_price for item in items)

    # Validate total price is not zero
    if total_price <= 0:
        messages.error(request, "Order total cannot be zero. Please check item prices.")
        return redirect("cart_view")

    if request.method == "POST":
        delivery_date = request.POST.get("delivery_date")
        payment_method = request.POST.get("payment_option")
        delivery_option = request.POST.get("delivery_method")

        # Validate delivery date
        try:
            delivery_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
            today = datetime.today().date()
            max_date = today + timedelta(days=30)
            
            if delivery_date < today:
                messages.error(request, "Delivery date cannot be in the past.")
                return redirect("checkout_view")
            elif delivery_date > max_date:
                messages.error(request, "Delivery date must be within the next 30 days.")
                return redirect("checkout_view")
        except (ValueError, TypeError):
            messages.error(request, "Please select a valid delivery date.")
            return redirect("checkout_view")

        # Calculate final price with delivery
        final_price = total_price
        if delivery_option == "express":
            final_price += Decimal("500.00")

        # Final price validation
        if final_price <= 0:
            messages.error(request, "Order total cannot be zero. Please check item prices.")
            return redirect("cart_view")

        try:
            # Create the order
            order = Order.objects.create(
                user=request.user,
                batch=items[0].chick_batch,
                one_kg_count=sum(item.one_kg_count for item in items),
                two_kg_count=sum(item.two_kg_count for item in items),
                three_kg_count=sum(item.three_kg_count for item in items),
                payment_method=payment_method if payment_method in ["cod", "online", "upi"] else "cod",
                price=final_price,
                delivery_option=delivery_option,
                delivery_date=delivery_date,
                status="pending",
            )

            # Clear the cart after successful order creation
            cart.items.all().delete()
            cart.save()

            # Send confirmation email
            send_order_confirmation_email(request.user.email, order)
            
            messages.success(request, "Order placed successfully!")
            return redirect("view_orders")

        except Exception as e:
            messages.error(request, f"Error creating order: {str(e)}")
            return redirect("checkout_view")

    context = {
        "cart": cart,
        "items": items,
        "total_price": total_price,
        "total_discounted": total_discounted,
    }
    return render(request, "hoteldetials/checkout_view.html", context)


def view_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "hoteldetials/orderview.html", {"orders": orders})

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(email,order):
    # Prepare the context with order details
    context = {
        'order': order,
        'total_price': order.total_price(),  # Call the total_price method
        'delivery_option': order.delivery_option,
        'delivery_date': order.delivery_date,
    }

    # Render the HTML content using the template
    subject = f"Order Confirmation - Order ID: {order.id}"
    message = render_to_string('orderconfirmation.html', context)

    # Send the email
    send_mail(
        subject=subject,
        message='',  # Leaving the plain-text message empty as we're using HTML
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.user.email],
        html_message=message,  # HTML content
    )
from django.http import HttpResponse
from .models import Order

def place_order(request):
    if request.method == 'POST':
        # Get the batch and validate price
        batch = get_object_or_404(ChickBatch, id=request.POST.get('batch_id'))
        
        # Ensure price is set and not zero
        if not batch.price_per_kg or float(batch.price_per_kg) <= 0:
            messages.error(request, "Invalid price. Please contact the administrator.")
            return redirect('cart_view')

        # Calculate total price
        quantity = int(request.POST.get('quantity', 0))
        total_price = float(batch.price_per_kg) * quantity

        if total_price <= 0:
            messages.error(request, "Order total cannot be zero.")
            return redirect('cart_view')

        # Create order with validated price
        order = Order.objects.create(
            user=request.user,
            batch=batch,
            quantity=quantity,
            price=total_price,
            delivery_option='standard',
            delivery_date='2025-01-25',
            status='pending'
        )

        # Send confirmation email
        send_order_confirmation_email(request.user.email, order)
        
        messages.success(request, "Order placed successfully!")
        return redirect('order_success')

    return redirect('cart_view')

@login_required
def wallet_view(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    context = {
        'wallet': request.user.wallet,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'user': request.user
    }
    return render(request, 'hoteldetials/wallet.html', context)




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
from decimal import Decimal

@csrf_exempt
def add_funds_to_wallet(request):
    if request.method == "POST":
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Create Razorpay Order first
            amount = int(float(request.POST.get('amount', 0)) * 100)  # Convert to paise
            currency = 'INR'
            
            # Create order
            order_data = {
                'amount': amount,
                'currency': currency,
                'payment_capture': 1  # Auto capture payment
            }
            order = client.order.create(data=order_data)
            
            if order['id']:
                payment_id = request.POST.get('payment_id')
                
                # Verify payment if signature is provided
                if 'signature' in request.POST:
                    params_dict = {
                        'razorpay_payment_id': payment_id,
                        'razorpay_order_id': order['id'],
                        'razorpay_signature': request.POST.get('signature')
                    }
                    client.utility.verify_payment_signature(params_dict)
                
                # Update wallet
                amount_in_rupees = float(amount) / 100
                wallet = request.user.wallet
                wallet.balance += amount_in_rupees
                wallet.save()
                
                # Create transaction record
                WalletTransaction.objects.create(
                    user=request.user,
                    amount=amount_in_rupees,
                    transaction_type='credit',
                    status='completed',
                    payment_id=payment_id,
                    description='Wallet recharge'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Funds added successfully',
                    'new_balance': str(wallet.balance)
                })
            
            return JsonResponse({
                'success': False,
                'error': 'Could not create order'
            }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
@require_http_methods(["POST"])
def add_funds(request):
    try:
        amount = float(request.POST.get('amount', 0))
        # Add your logic to update wallet balance
        # For example:
        request.user.wallet.balance += amount
        request.user.wallet.save()
        
        return JsonResponse({
            'success': True,
            'new_balance': request.user.wallet.balance
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["GET"])
def get_balance(request):
    try:
        return JsonResponse({
            'success': True,
            'balance': request.user.wallet.balance
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
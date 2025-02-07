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

def hoteldashboard(request):
    batch_type = request.GET.get("batch_type", "")
    query = request.GET.get("q", "")
    max_distance = request.GET.get("max_distance", None)

    # Get user coordinates from request (fallback to hotel user's stored data)
    user_lat = request.GET.get("latitude") or None
    user_lon = request.GET.get("longitude") or None

    hoteluser = HotelUser.objects.filter(hotel_owner=request.user).first()
    if not user_lat or not user_lon:
        user_lat = hoteluser.latitude
        user_lon = hoteluser.longitude

    # Debugging: Print user coordinates
    print(f"User Latitude: {user_lat}, User Longitude: {user_lon}")

    # Validate user coordinates
    try:
        user_lat = float(user_lat)
        user_lon = float(user_lon)
        if not (-90 <= user_lat <= 90) or not (-180 <= user_lon <= 180):
            raise ValueError("Invalid latitude or longitude values.")
    except (ValueError, TypeError) as e:
        messages.error(request, f"Invalid location data: {e}. Please check your coordinates.")
        return redirect("some_error_handling_view")  # Redirect to an appropriate error handling view

    farms = Farm.objects.all()

    if batch_type:
        farms = farms.filter(chick_batches__batch_type=batch_type).distinct()
    if query:
        farms = farms.filter(name__icontains=query)

    recommended_farms = []

    # Calculate and filter farms based on distance
    for farm in farms:
        if farm.latitude and farm.longitude:
            origin = (user_lat, user_lon)
            destination = (farm.latitude, farm.longitude)

            # Debugging: Print origin and destination
            print(f"Origin: {origin}, Destination: {destination}")

            distance = calculate_distance(origin, destination)

            farm.distance = round(distance, 2)  # Distance in km

            if max_distance and distance <= float(max_distance):
                recommended_farms.append(farm)
            elif not max_distance and distance <= 50:  # Default 50 km limit
                recommended_farms.append(farm)

    # Sort farms by distance (nearest first)
    recommended_farms.sort(key=lambda x: x.distance)

    paginator = Paginator(recommended_farms, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "hoteldetials/farmlist.html", {
        "page_obj": page_obj,
        "hotel_name": hoteluser.hotel_name,
        "batch_type": batch_type,
    })


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


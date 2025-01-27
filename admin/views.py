from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import FeedRequest, Supplier

def manage_feed_requests(request):
    feed_requests = FeedRequest.objects.all().order_by('-requested_date')
    suppliers = Supplier.objects.filter(is_active=True)
    
    return render(request, 'admin/manage_feed_requests.html', {
        'feed_requests': feed_requests,
        'suppliers': suppliers
    })

def assign_supplier(request, request_id):
    if request.method == 'POST':
        feed_request = FeedRequest.objects.get(id=request_id)
        supplier_id = request.POST.get('supplier')
        price_per_unit = request.POST.get('price_per_unit')

        feed_request.assigned_supplier_id = supplier_id
        feed_request.price_per_unit = price_per_unit
        feed_request.status = 'assigned'
        feed_request.assigned_date = timezone.now()
        feed_request.save()

        # Generate bill
        feed_request.generate_bill()
        
        messages.success(request, 'Supplier assigned and bill generated successfully!')
        return redirect('manage_feed_requests') 
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from .views import buy_batch

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stakeholder.urls')),
    path('buy-batch/<int:batch_id>/', buy_batch, name='buy_batch'),
    # ... your other URL patterns ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
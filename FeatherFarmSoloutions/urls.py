from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from stakeholder.views import logout_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stakeholder.urls')),
    path('hotel/', include('hoteldetails.urls')),
    path('accounts/', include('allauth.urls')),
    path('logout/', logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
#     path('', include('two_factor.urls')),



]

# Serve media files in debug mode
if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += [
        path('media/<path:path>/', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

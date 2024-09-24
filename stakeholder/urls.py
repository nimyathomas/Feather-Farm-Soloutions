from django.urls import path
from user.views import register, CustomLoginView, admindash, stakeholderuser, customeruser, stakeholderuserprofile, customeruserprofile, stakeholder_registration, delete_user
from .import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('about/contact/', views.contact, name='about_contact'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', register, name='signup'),
    path('stakeholder/', views.stakeholder, name='stakeholder'),
    path('stateholder_batch/', views.stateholder_batch, name='stateholder_batch'),
    path('admindash/', admindash, name='admindash'),
    path('stakeholderuser/', stakeholderuser, name='stakeholderuser'),
    path('customeruser/', customeruser, name='customeruser'),
    path('stakeholderuserprofile/<int:id>',
         stakeholderuserprofile, name='stakeholderuserprofile'),
    path('feed_request/<int:user_id>/',views.feed_request, name='feed_request'),
    path('update-chick-count/<int:id>/',
         views.update_chick_count, name='update_chick_count'),
    path('customeruserprofile/<int:id>',
         customeruserprofile, name='customeruserprofile'),
    path('stakeholder_registration/<int:id>/',
         stakeholder_registration, name='stakeholder_registration'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
]

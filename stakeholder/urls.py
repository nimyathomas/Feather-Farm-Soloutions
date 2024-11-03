from django.urls import path
from user.views import approve_order, download_daily_log, register, CustomLoginView, admindash, stakeholderuser, customeruser, stakeholderuserprofile, customeruserprofile, stakeholder_registration, vaccine_admin, feed_admin, renew_pollution_certificate, supplier_list, add_supplier, enable_supplier, disable_supplier, edit_supplier, toggle_user_status,view_stakeholder_view
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
    path('view_stakeholder_view/<int:id>', view_stakeholder_view, name='view_stakeholder_view'),
    path('chick_batches/download/<int:batch_id>/', download_daily_log, name='download_daily_log'),
    path('feed_dashboard_view/<int:user_id>/',
         views.feed_dashboard_view, name='feed_dashboard_view'),
    path('update-chick-count/<int:id>/',
         views.update_chick_count, name='update_chick_count'),
    path('customeruserprofile/<int:id>',
         customeruserprofile, name='customeruserprofile'),
    path('approve_order/<int:order_id>/', approve_order, name='approve_order'),
    path('stakeholder_registration/<int:id>/',
         stakeholder_registration, name='stakeholder_registration'),
    path('vaccination/<int:user_id>/', views.vaccination, name='vaccination'),
    path('vaccine_admin/', vaccine_admin, name='vaccine_admin'),
    path('feed_admin/', feed_admin, name='feed_admin'),
    path('renew-certificate/<int:user_id>/',
         renew_pollution_certificate, name='renew_certificate'),
    path('add_daily_data', views.add_daily_data, name='add_daily_data'),
    path('batch/<int:batch_id>/daily-data/',
         views.list_daily_data, name='list_daily_data'),
    path('edit_daily_data/<int:id>/',
         views.edit_daily_data, name='edit_daily_data'),
    path('delete-entry/<int:daily_data_id>/',
         views.delete_daily_data, name='delete_daily_data'),
    path('daily_feed_summary/', views.daily_feed_summary,
         name='daily_feed_summary'),
    path('batch_feed_summary/', views.batch_feed_summary,
         name='batch_feed_summary'),
    path('supplier_list', supplier_list, name='supplier_list'),
    path('add_supplier', add_supplier, name='add_supplier'),
    path('edit_supplier/<int:supplier_id>/', edit_supplier,
         name='edit_supplier'),  # Ensure the URL accepts an ID

    path('enable_supplier/<int:supplier_id>/',
         enable_supplier, name='enable_supplier'),  # Add this
    path('disable_supplier/<int:supplier_id>/',
         disable_supplier, name='disable_supplier'),  # Add this
    path('toggle_user_status/<int:user_id>/',
         toggle_user_status, name='toggle_user_status'),
    path('supplier_list', views.supplier_list, name='supplier_list'),

]

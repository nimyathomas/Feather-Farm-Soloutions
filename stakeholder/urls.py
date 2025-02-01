from django.urls import path

from user.views import (
    approve_order,
    download_daily_log,
    register,
    CustomLoginView,
    admindash,
    stakeholderuser,
    customeruser,
    stakeholderuserprofile,
    customeruserprofile,
    vaccine_admin,
    feed_admin,
    renew_pollution_certificate,
    supplier_list,
    add_supplier,
    enable_supplier,
    disable_supplier,
    edit_supplier,
    toggle_user_status,
    view_stakeholder_view,
    manage_vaccines,
    add_vaccine,
    edit_vaccine,
    manage_records,
    add_record,
    vaccine_dashboard,
    delete_vaccine,
    assign_vaccine,
    get_active_batches,
    add_resource,
    add_tip,
    waste_management_admin,
    view_resources,
    view_tips,
    # chat_api,
    # chat_room
#     update_location,
)
from . import views 

# app_name='stakeholder'
urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("about/contact/", views.contact, name="about_contact"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", register, name="signup"),
    path("stakeholder/", views.stakeholder, name="stakeholder"),
    path("stateholder_batch/", views.stateholder_batch, name="stateholder_batch"),
    path("admindash/", admindash, name="admindash"),
    path("stakeholderuser/", stakeholderuser, name="stakeholderuser"),
    path("customeruser/", customeruser, name="customeruser"),
    path(
        "stakeholderuserprofile/<int:id>",
        stakeholderuserprofile,
        name="stakeholderuserprofile",
    ),
    path(
        "view_stakeholder_view/<int:id>",
        view_stakeholder_view,
        name="view_stakeholder_view",
    ),
    path(
        "chick_batches/download/<int:batch_id>/",
        download_daily_log,
        name="download_daily_log",
    ),
    path(
        "feed_dashboard_view/<int:user_id>/",
        views.feed_dashboard_view,
        name="feed_dashboard_view",
    ),
    path(
        "update-chick-count/<int:id>/",
        views.update_chick_count,
        name="update_chick_count",
        
    ),
    path(
        "customeruserprofile/<int:id>", customeruserprofile, name="customeruserprofile"
    ),
    path("approve_order/<int:order_id>/", approve_order, name="approve_order"),
    path(
        "stakeholder_registration/<int:id>/",
        views.add_or_edit_farm,
        name="stakeholder_registration",
    ),
    path("vaccination/<int:user_id>/", views.vaccination, name="vaccination"),
    path("vaccine_admin/", vaccine_admin, name="vaccine_admin"),
    
    
    # path("forum/", views.forum_dashboard, name="forum_dashboard"),
    # path('forum/<int:post_id>/', views.forum_dashboard, name='forum_dashboard'),
    
    path("forum/", views.forum_dashboard, name="forum_dashboard"),
    path("forum/<int:post_id>/", views.forum_dashboard, name="forum"),
    
    path('forum/delete/<int:post_id>/', views.delete_post, name='delete_post'),

    
    
    path("feed_admin/", feed_admin, name="feed_admin"),
    path(
        "renew-certificate/<int:user_id>/",
        renew_pollution_certificate,
        name="renew_certificate",
    ),
    path("add_daily_data", views.add_daily_data, name="add_daily_data"),
    path(
        "batch/<int:batch_id>/daily-data/",
        views.list_daily_data,
        name="list_daily_data",
    ),
    path("edit_daily_data/<int:id>/", views.edit_daily_data, name="edit_daily_data"),
    path(
        "delete-entry/<int:daily_data_id>/",
        views.delete_daily_data,
        name="delete_daily_data",
    ),
    path("daily_feed_summary/", views.daily_feed_summary, name="daily_feed_summary"),
    path("batch_feed_summary/", views.batch_feed_summary, name="batch_feed_summary"),
    path("supplier_list", supplier_list, name="supplier_list"),
    path("add_supplier", add_supplier, name="add_supplier"),
    path(
        "edit_supplier/<int:supplier_id>/", edit_supplier, name="edit_supplier"
    ),  # Ensure the URL accepts an ID
    path(
        "enable_supplier/<int:supplier_id>/", enable_supplier, name="enable_supplier"
    ),  # Add this
    path(
        "disable_supplier/<int:supplier_id>/", disable_supplier, name="disable_supplier"
    ),  # Add this
    path(
        "toggle_user_status/<int:user_id>/",
        toggle_user_status,
        name="toggle_user_status",
    ),
    path("supplier_list", views.supplier_list, name="supplier_list"),
    path("vaccines/", manage_vaccines, name="manage_vaccines"),
    path("vaccines/add/", add_vaccine, name="add_vaccine"),
    path("vaccines/edit/<int:vaccine_id>/", edit_vaccine, name="edit_vaccine"),
    path("records/", manage_records, name="manage_records"),
    path("records/add/", add_record, name="add_record"),
    path("vaccines/dashboard/", vaccine_dashboard, name="vaccine_dashboard"),
    path("delete-vaccine/<int:vaccine_id>/", delete_vaccine, name="delete_vaccine"),
    path("assign-vaccine/", assign_vaccine, name="assign_vaccine"),
    path(
        "get-active-batches/<int:user_id>/",
        get_active_batches,
        name="get_active_batches",
    ),
    path("waste-management/", waste_management_admin, name="waste_management_admin"),
    path("waste-management/add-resource/", add_resource, name="add_resource"),
    path("waste-management/add-tip/", add_tip, name="add_tip"),
    path("waste-management/resources/", view_resources, name="view_resources"),
    path("waste-management/tips/", view_tips, name="view_tips"),
    
    path('chat/<str:room_name>/',views.chat_room, name='chat_room'),

    
    # path('api/chat/',views.chat_api, name='chat_api')
    
    path("chick-health-recognition/", views.chick_health_recognition, name="chick_health_recognition"),

    
   
]

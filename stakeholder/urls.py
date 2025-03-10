from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views 
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
    get_vaccine,
    vaccine_stock_level,
    order_analytics,farm_analytics_dashboard,contract_dashboard,create_contract,view_contracts,
    get_farm_details,contract_detail,generate_contract_pdf,sign_contract,admin_chat_view,stakeholder_chat_view,get_chat_messages,send_message  
   
)
from .views import stakeholder_vaccination_list  # Remove scan_qr_code from import

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
    path("vaccination-main/", views.vaccination_main, name="vaccination_main"),
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
    # path("vaccines/dashboard/", vaccine_dashboard, name="vaccine_dashboard"),
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
    
    # Chat URLs - using views from user.views
   
    path('api/chat/', views.chat_api, name='chat_api'),
    
    # path("chick-health-recognition/", views.chick_health_recognition, name="chick_health_recognition"),
    # path('chat/handle/', views.handle_chat, name='handle_chat'),
    path('manage-vaccines/', views.manage_vaccines, name='manage_vaccines'),
    # path('schedule-vaccination/', views.schedule_vaccination, name='schedule_vaccination'),
    # path('delete-schedule/<int:schedule_id>/', views.delete_vaccination_schedule, name='delete_schedule'),
    path('add-vaccine/', views.add_vaccine, name='add_vaccine'),
    path('edit-vaccine/<int:vaccine_id>/', edit_vaccine, name='edit_vaccine'),
    path('delete-vaccine/<int:vaccine_id>/', delete_vaccine, name='delete_vaccine'),
    path('get-vaccine/<int:vaccine_id>/', get_vaccine, name='get_vaccine'),
    path('vaccine-stock-level/', vaccine_stock_level, name='vaccine_stock_level'),
    # path('disease-analysis/', views.disease_analysis_list, name='disease_analysis_list'),
    # path('disease-analysis/<int:analysis_id>/', views.disease_analysis_detail, name='disease_analysis_detail'),
    # path('analysis/<int:analysis_id>/feedback/', views.provide_feedback, name='provide_feedback'),
    path('batch/<uuid:batch_uuid>/detail/', views.batch_detail_qr, name='batch_detail_qr'),
    path('batches/qrcodes/', views.view_batch_qrcodes, name='view_batch_qrcodes'),
    # path('test-media/<str:filename>/', views.test_media, name='test_media'),
    path('feed-main-dashboard/', views.feed_main_dashboard, name='feed_main_dashboard'),
    
    
    path('feed/manage/', views.feed_manage, name='feed_manage'),

    path('feed-dashboard/', views.feed_dashboard, name='feed_dashboard'),
    path('feed-manage/', views.feed_manage, name='feed_manage'),
    path('feed-stock/add/', views.add_feed_stock, name='add_feed_stock'),

    path('feed-stock/create/', views.feed_stock_create, name='feed_stock_create'),

    
    path('feed-stock/update/<int:feed_id>/', 
         views.update_feed_stock_view, 
         name='update_feed_stock'),
    path('feed-stock/delete/<int:feed_id>/', 
         views.delete_feed_stock, 
         name='delete_feed_stock'),
    path('api/calculate-feed/<int:chick_count>/', views.calculate_feed, name='calculate_feed'),
    
    path('feed/delete/<int:feed_id>/', views.delete_feed_stock, name='delete_feed_stock'),
    
    path('feed/active-batches/', views.active_batches_feed, name='active_batches_feed'),
    path('feed/batch-assignment/<int:batch_id>/', 
         views.batch_feed_assignment, 
         name='batch_feed_assignment'),
    path('feed-tracking/', views.feed_tracking_dashboard, name='feed_tracking_dashboard'),
    path('feed/acknowledge/<int:assignment_id>/', views.acknowledge_feed_assignment, name='acknowledge_feed_assignment'),
    path('record-feed/<int:batch_id>/', views.record_feed_consumption, name='record_feed_consumption'),
    path('vaccine/<int:vaccine_id>/details/', views.get_vaccine_details, name='vaccine_details'),
    path('vaccine/<int:vaccine_id>/update/', views.update_vaccine, name='update_vaccine'),
    path('vaccine/<int:vaccine_id>/delete/', views.delete_vaccine, name='delete_vaccine'),
    
    



    path('vaccinations/', views.vaccination_list, name='vaccination_list'),
    path('vaccinations/assign/', views.assign_vaccination, name='assign_vaccination'),
    path('vaccinations/delete/<int:schedule_id>/', views.delete_vaccination, name='delete_vaccination'),
    
    path('vaccinations/edit/<int:schedule_id>/', views.edit_vaccination, name='edit_vaccination'),
    path('vaccinations/<int:pk>/scan/', views.scan_qr_code, name='stakeholder_scan_qr'),
    path('vaccinations/<int:pk>/evidence/', 
         views.upload_vaccination_evidence, 
         name='upload_vaccination_evidence'),
    
    path('my-vaccinations/', views.stakeholder_vaccination_list, name='stakeholder_vaccination_list'),
    
    path('my-vaccinations/', 
         views.stakeholder_vaccination_list, 
         name='stakeholder_vaccination_list'),
    
    path('vaccination/<int:schedule_id>/validate-vial/', 
         views.validate_vaccine_vial, 
         name='validate_vaccine_vial'),
    
    
    path('feed/manage/', views.feed_manage, name='feed_manage'),
    
    path('order-analytics/', order_analytics, name='order_analytics'),
    path('farm-analytics-dashboard/', farm_analytics_dashboard, name='farm_analytics_dashboard'),    
    path('feed/daily-report/<str:date>/', views.daily_feed_report, name='daily_feed_report'),
    path('feed/report-pdf/<str:date>/', views.daily_feed_report, name='feed_report_pdf'),
    
    
    
#contract

     path('contracts/dashboard/', contract_dashboard, name='contract_dashboard'),
     path('contracts/create/', create_contract, name='create_contract'),
     path('contracts/view/', view_contracts, name='view_contracts'),
     
    path('get-farm-details/', get_farm_details, name='get_farm_details'),
    path('contracts/<int:contract_id>/',contract_detail, name='contract_detail'),
    path('contracts/generate-pdf/<int:contract_id>/',generate_contract_pdf, name='generate_contract_pdf'),
   
    path('contracts/sign/<int:contract_id>/', sign_contract, name='sign_contract'),
    
    path('growth-prediction/', views.growth_prediction_dashboard, name='growth_prediction_dashboard'),
    path('predict-weight/', views.predict_weight, name='predict_weight'),
    path('prediction-history/<int:batch_id>/', views.prediction_history, name='prediction_history'),
    path('day-prediction/<int:batch_id>/<int:day_number>/', views.day_prediction, name='day_prediction'),
    # path('get-batch-alive-count/<int:batch_id>/', views.get_batch_alive_count, name='get_batch_alive_count'),
    
    # ... existing urls ...

# Chat URLs
    path('chat/admin/', admin_chat_view, name='admin_chat_view'),
    path('chat/stakeholder/', stakeholder_chat_view, name='stakeholder_chat_view'),
    path('chat/<int:room_id>/messages/', get_chat_messages, name='get_chat_messages'),
    # path('chat/<int:room_id>/mark-read/', mark_messages_read, name='mark_messages_read'),
    # path('chat/unread-count/', get_unread_message_count, name='get_unread_message_count'),
    path('chat/<int:room_id>/send/',send_message, name='send_message'),  # Add this line
# ... existing urls ...
    
    path('feed/day-consumption/<int:batch_id>/<int:day_number>/', 
         views.day_feed_consumption, 
         name='day_feed_consumption'),
    
    path('feed/batch-info/<int:batch_id>/', views.batch_feed_info, name='batch_feed_info'),
    
    path('batch/<int:batch_id>/feed-assignments/', 
         views.get_feed_assignments, 
         name='get_feed_assignments'),
    
    
    

    # ... other urls ...
    path('fcr-dashboard/', views.stakeholder_dashboard, name='fcr_dashboard'),
    path('batch/<int:batch_id>/complete/', views.complete_batch, name='complete_batch'),
    path('batch/<int:batch_id>/recalculate/', views.recalculate_batch_metrics, name='recalculate_batch_metrics'),
    
    
    

    # ... existing URLs ...
    path('payments/', views.stakeholder_payments_view, name='stakeholder_payments'),
    path('payment/<int:payment_id>/', views.payment_details, name='payment_details'),
    path('payment/create/<int:batch_id>/', views.create_payment, name='create_payment'),
    path('payment/process/<int:payment_id>/', views.process_payment, name='process_payment'),
    path('payment/callback/', views.razorpay_callback, name='razorpay_callback'),  # Add this line


    path('download-bill/<int:payment_id>/', views.download_bill, name='download_bill'),
    # Check your urlpatterns = [
    path('stakeholder/', views.stakeholderdash, name='stakeholder_dashboard'),  # Verify this pattern
    path('generate-bill/<int:batch_id>/', views.generate_bill, name='generate_bill'),
    path('export-fcr-data/<str:format>/', views.export_fcr_data, name='export_fcr_data'),
    
    path('chick-health-recognition/', views.chick_health_recognition, name='chick_health_recognition'),
    # path('analysis/<int:analysis_id>/details/', 
    #      views.get_analysis_details, 
    #      name='analysis_details'),
    path('analysis-details/<int:analysis_id>/', views.analysis_details_page, name='analysis_details'),
    path('analysis-report/<int:analysis_id>/', views.generate_analysis_report, name='analysis_report'),

    #path('provide-feedback/<int:analysis_id>/', views.provide_feedback, name='provide_feedback'),
    
    # It might look something like this:
    
    path('stakeholder/orders/', views.stakeholder_order_dashboard, name='stakeholder_order_dashboard'),
    path('stakeholder/orders/<int:order_id>/update-delivery/', 
         views.update_delivery_status, 
         name='update_delivery_status'),    


    
]

    
    


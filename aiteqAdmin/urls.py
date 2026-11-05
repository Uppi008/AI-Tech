from django.urls import path
from aiteqAdmin.views import *

urlpatterns = [
    path('',base,name='dashboard'),
    path('general-settings/',General_Settings,name='general_settings'),
    path('dashboard/',dashboard,name='dashboard'),
    
    path('console_signin/', console_auth, name="console_signin"),
    path('console_logout/', console_logout, name='console_logout'),
    
        # Services URLs
    path('services/', service_list, name='service_list'),
    path('get-service-details/', get_details_service, name='get_details_service'),
    path('get-service-details/', get_details_service, name='get_service_details'),
    path('service-update/<int:id>/', update_service, name='service_update'),
    path('service-delete/<int:id>/', delete_service, name='service_delete'),
    path('service/status/<int:service_id>/', toggle_service_status, name='toggle_service_status'),
    path('service/report/', get_service_report, name='get_service_report'),
    path('service/bulk-upload/', bulk_upload_service, name='bulk_upload_service'),
    
    path('supporting-service/', supporting_service_list, name='supporting_service_list'),
    path('get-details-supporting-service/', get_details_supporting_service, name='get_details_supporting_service'),
    path('supporting-service-update/<int:id>/', update_supporting_service, name='supporting_service_update'),
    path('supporting-service-delete/<int:id>/', delete_supporting_service, name='supporting_service_delete'),
    path('supporting-service/status/<int:supporting_service_id>/', toggle_supporting_service_status, name='toggle_supporting_service_status'),
    path('supporting-service/report/', get_supporting_service_report, name='get_supporting_service_report'),
    path('supporting-service/bulk-upload/', bulk_upload_supporting_service, name='bulk_upload_supporting_service'),
    
    path('service-consultation/', service_consultation_list, name='service_consultation_list'),
    path('get-details-service-consultation/', get_details_service_consultation, name='get_details_service_consultation'),
    path('service-consultation-update/<str:id>/', update_service_consultation, name='service_consultation_update'),
    path('service-consultation-delete/<str:id>/', delete_service_consultation, name='service_consultation_delete'),
    path('service-consultation/status/<int:consultation_id>/', toggle_service_consultation_status, name='toggle_service_consultation_status'),  
    
    path('testimonials/', testimonial_list, name='testimonial_list'),
    path('get-testimonial-details/', get_details_testimonial, name='get_details_testimonial'),
    path('testimonial-update/<str:id>/', update_testimonial, name='testimonial_update'),            
    path('testimonial-delete/<str:id>/', delete_testimonial, name='testimonial_delete'),
    path('testimonial/status/<int:testimonial_id>/', toggle_testimonial_status, name='toggle_testimonial_status'),  
    
    path('project_category_list/', project_category_list, name='project_category_list'),
    path('get_project_category_details/', get_project_category_details, name='get_project_category_details'),
    path('update_project_category/<str:id>/', update_project_category, name='update_project_category'),
    path('delete_project_category/<str:id>/', delete_project_category, name='delete_project_category'),
    path('toggle_project_category_status/<int:category_id>/', toggle_project_category_status, name='toggle_project_category_status'), 
    
    path('portfolio_project_list/', portfolio_project_list, name='portfolio_project_list'),
    path('get_portfolio_project_details/', get_portfolio_project_details, name='get_portfolio_project_details'),
    path('update_portfolio_project/<str:id>/', update_portfolio_project, name='update_portfolio_project'),
    path('delete_portfolio_project/<str:id>/', delete_portfolio_project, name='delete_portfolio_project'),
    path('toggle_portfolio_project_status/<int:project_id>/', toggle_portfolio_project_status, name='toggle_portfolio_project_status'), 
    
    path('contact-info/', contact_info_edit, name='contact_info_edit'),

    path('result-statistics/', result_statistic_list, name='result_statistic_list'),
    path('get-details-result-statistic/', get_details_result_statistic, name='get_details_result_statistic'),
    path('result-statistic-update/<int:id>/', update_result_statistic, name='result_statistic_update'),
    path('result-statistic-delete/<int:id>/', delete_result_statistic, name='result_statistic_delete'),
    path('result-statistic/status/<int:stat_id>/', toggle_result_statistic_status, name='toggle_result_statistic_status'),

    path('contact-messages/', contact_message_list, name='contact_message_list'),
    path('get-contact-message-details/', get_contact_message_details, name='get_contact_message_details'),
    path('contact-message-update/<str:id>/', update_contact_message, name='update_contact_message'),
    path('contact-message-delete/<str:id>/', delete_contact_message, name='delete_contact_message'),
    path('contact-message/status/<int:message_id>/', toggle_contact_message_status, name='toggle_contact_message_status'),  

        
    

    
    

    
    


]   

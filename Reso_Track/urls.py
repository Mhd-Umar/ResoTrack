from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Landing & Auth
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('lab-admin-dashboard/', views.lab_admin_dashboard, name='lab_admin_dashboard'),
    
    # Common Profiling
    path('profile/', views.profile_view, name='profile'),
    
    # User Modules
    path('resources/', views.resource_analyzer, name='resources'),
    path('complaints/add/', views.add_complaint, name='add_complaint'),
    path('complaints/status/', views.complaint_status, name='complaint_status'),
    path('suggestions/add/', views.add_suggestion, name='add_suggestion'),
    path('complaints/delete/<int:c_id>/', views.delete_complaint, name='delete_complaint'),
    path('suggestions/delete/<int:s_id>/', views.delete_suggestion, name='delete_suggestion'),
    
    # Admin Modules
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/remove/<int:user_id>/', views.admin_remove_user, name='admin_remove_user'),
    path('admin-panel/users/block/<int:user_id>/', views.admin_block_user, name='admin_block_user'),
    path('admin-panel/labs/', views.admin_labs, name='admin_labs'),
    path('admin-panel/complaints/', views.admin_complaints, name='admin_complaints'),
    path('admin-panel/complaints/approve/<int:c_id>/', views.admin_approve_complaint, name='admin_approve_complaint'),
    path('admin-panel/complaints/reject/<int:c_id>/', views.admin_reject_complaint, name='admin_reject_complaint'),
    path('admin-panel/suggestions/', views.admin_suggestions, name='admin_suggestions'),
    path('admin-panel/reports/', views.admin_reports, name='admin_reports'),
    path('admin-panel/complaints/delete/<int:c_id>/', views.admin_delete_complaint, name='admin_delete_complaint'),
    path('admin-panel/suggestions/delete/<int:s_id>/', views.admin_delete_suggestion, name='admin_delete_suggestion'),
    path('admin-panel/enquiries/', views.admin_enquiries, name='admin_enquiries'),
    path('admin-panel/settings/', views.admin_settings, name='admin_settings'),
    path('admin-panel/sliders/', views.admin_sliders, name='admin_sliders'),
    path('admin-panel/sliders/add/', views.admin_add_slider, name='admin_add_slider'),
    path('admin-panel/sliders/edit/<int:s_id>/', views.admin_edit_slider, name='admin_edit_slider'),
    path('admin-panel/sliders/delete/<int:s_id>/', views.admin_delete_slider, name='admin_delete_slider'),
    path('admin-panel/enquiries/reply/<int:e_id>/', views.admin_reply_enquiry, name='admin_reply_enquiry'),
    path('admin-panel/labs/edit/<int:l_id>/', views.admin_edit_lab, name='admin_edit_lab'),
    path('admin-panel/labs/delete/<int:l_id>/', views.admin_delete_lab, name='admin_delete_lab'),
    path('admin-panel/labs/admin/edit/<int:user_id>/', views.admin_edit_lab_admin, name='admin_edit_lab_admin'),
    path('admin-panel/labs/admin/delete/<int:user_id>/', views.admin_delete_lab_admin, name='admin_delete_lab_admin'),
    
    # Lab Admin Modules
    path('lab-panel/resources/add/', views.lab_add_resource, name='lab_add_resource'),
    path('lab-panel/resources/edit/<int:r_id>/', views.lab_edit_resource, name='lab_edit_resource'),
    path('lab-panel/resources/delete/<int:r_id>/', views.lab_delete_resource, name='lab_delete_resource'),
    path('lab-panel/complaints/', views.lab_complaints, name='lab_complaints'),
    path('lab-panel/complaints/update/<int:c_id>/<str:status>/', views.lab_update_complaint, name='lab_update_complaint'),
    path('lab-panel/suggestions/', views.lab_suggestions, name='lab_suggestions'),
    path('lab-panel/stocks/', views.lab_stocks, name='lab_stocks'),
    path('lab-panel/stocks/print/', views.lab_stocks_print, name='lab_stocks_print'),
    path('lab-panel/stocks/add/', views.lab_add_stock, name='lab_add_stock'),
    path('lab-panel/stocks/edit/<int:s_id>/', views.lab_edit_stock, name='lab_edit_stock'),
    path('lab-panel/stocks/delete/<int:s_id>/', views.lab_delete_stock, name='lab_delete_stock'),
]

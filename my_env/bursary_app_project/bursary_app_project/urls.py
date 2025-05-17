"""
URL configuration for bursary_app_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from bursary_app import views
from django.contrib.auth.views import LoginView,LogoutView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view, name="home"),
    path('aboutclick', views.about_view, name='aboutclick'),
    
    path('adminclick', views.adminclick_view),
    path('studentclick', views.studentclick_view),
    

    path('adminsignup',views.admin_signup_view),
    path('studentsignup',views.student_signup_view),

    path('adminlogin', LoginView.as_view(template_name='bursary/adminlogin.html')),
    path('studentlogin', LoginView.as_view(template_name='bursary/studentlogin.html')),

    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout', views.logout_view, name='logout'),
    

    path('admin-add-scheme', views.admin_add_scheme_view, name='admin-add-scheme'),
    path('admin-manage-users',views.admin_manage_users, name='admin-manage-users'),
    path('admin-delete-user/<str:id_number>',views.delete_user, name='admin-delete-user'),
    path('admin-profile', views.admin_profile_view, name='admin-profile'),
    path('admin-settings', views.admin_settings_view, name='admin-settings'),
    path('scheme_list/', views.scheme_list, name='scheme_list'),
    path('edit_scheme/<int:scheme_id>/', views.admin_add_scheme_view, name='edit_scheme'),
    path('delete_scheme/<int:scheme_id>/', views.delete_scheme, name='delete_scheme'),
    path('admin-notice', views.admin_notice_view, name='admin-notice'),

    path('institution_applications/<str:institution_type>/', views.institution_applications, name='institution_applications'),

    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    path('all_applications', views.all_applications_view, name='all_applications'),
    path('export_fund_data', views.export_fund_data, name='export_fund_data'),
    path('admin_pending_applications', views.admin_pending_applications_view, name='admin_pending_applications'),
    path('review_applications/<int:application_id>/', views.review_application_view, name='review_applications'),
    

    path('approve/<int:app_id>/', views.approve_application, name='approve_application'),
    path('disburse-funds/', views.disburse_funds, name="disburse-funds"),
    path('approved_applications', views.approved_applications, name='approved_applications'),

    path('student-dashboard', views.student_dashboard_view,name='student-dashboard'),
    #path('student-attendance', views.student_attendance_view,name='student-attendance'),
    path('student-view-scheme', views.student_scheme_view,name='student-view-scheme'),
    path('application_form/<int:scheme_id>/', views.application_form, name='application_form'),
    path('application_success', views.application_success,name='application_success'),
    path('application_history', views.student_application_history, name='application_history'),
    path('application_detail/<int:application_id>/', views.application_detail, name='application_detail'),

    
    path('student-application-history', views.student_application_history, name='student-application-history'),

    path('change_password/', views.change_password, name='change_password'),

 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('', views.base, name='base'),
    path('', views.home, name='home'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<int:pk>/', views.portfolio_detail, name='portfolio_detail'),
    path('industries/', views.industries, name='industries'),
    
        # Admin Panel Access Credentials
    # path('login', views.login, name='login'),
    # path('forgot_password',views.forgotPassword,name='forgot_password'),

]

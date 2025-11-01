from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
import random
import string
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required


# Your existing views
# views.py
from django.shortcuts import render


# def base(request):
#     return render(request, 'AI_tech/base.html')

def home(request):
    from .models import Testimonial
    testimonials = Testimonial.objects.filter(is_active=True)
    featured_projects = PortfolioProject.objects.filter(is_active=True, is_featured=True)[:6]
    result_stats = ResultStatistic.objects.filter(is_active=True)[:4]
    categories = ProjectCategory.objects.filter(is_active=True)
    
    context = {
        'testimonials': testimonials,
        'portfolio': featured_projects,
        'result_stats': result_stats,
        'categories': categories,
    }
    return render(request, 'AI_tech/home.html', context)


def aboutus(request):
    return render(request, 'AI_tech/aboutus.html')

def portfolio(request):
    return render(request, 'AI_tech/portfolio.html')

def industries(request):
    return render(request, 'AI_tech/industries.html')

def contact(request):
    contact_data = ContactInfo.objects.first()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    return render(request, 'AI_tech/contact.html', {'contact_data': contact_data})


def services(request):
    services_list = Service.objects.all()
    
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        company_name = request.POST.get('company')
        description = request.POST.get('message')
        phone = request.POST.get('phone')
        
        try:
            # Create new consultation entry
            ServiceConsultation.objects.create(
                name=name,
                email=email,
                company_name=company_name,
                description=description,
                phone=phone
            )
            
            # Success message
            messages.success(request, 'Thank you! Your consultation request has been submitted successfully. We will contact you within 24 hours.')
            
            # Redirect to prevent form resubmission
            return redirect('services')
            
        except Exception as e:
            # Error message
            messages.error(request, 'Sorry, there was an error submitting your request. Please try again or contact us directly.')
    
    return render(request, 'AI_tech/services.html', {'services': services_list})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    
    form_result = services(request)
    if form_result is True:
        return redirect('service_detail', slug=slug)
    return render(request, 'AI_tech/service_detail.html', {'service': service})

def portfolio(request):
    portfolio_projects = PortfolioProject.objects.filter(is_active=True)
    result_stats = ResultStatistic.objects.filter(is_active=True)
    categories = ProjectCategory.objects.filter(is_active=True)
    
    context = {
        'portfolio_projects': portfolio_projects,
        'result_stats': result_stats,
        'categories': categories,
    }
    return render(request, 'AI_tech/portfolio.html', context)

def portfolio_detail(request, pk):
    project = get_object_or_404(PortfolioProject, id=pk, is_active=True)
    
    context = {
        'project': project,
    }
    return render(request, 'AI_tech/portfolio_detail.html', context)




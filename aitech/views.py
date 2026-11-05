from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.shortcuts import render, get_object_or_404


def home(request):
    try:
        testimonials = Testimonial.objects.filter(is_active=True)[:3]
        services_list = Service.objects.filter(status=True).order_by('-created_date')[:6]
        supporting_services = SupportingService.objects.filter(status=True)[:3]
        featured_projects = PortfolioProject.objects.filter(is_active=True, is_featured=True)[:3]
        result_stats = ResultStatistic.objects.filter(is_active=True, status=True)[:4]
        categories = ProjectCategory.objects.filter(is_active=True)[:6]
        
        context = {
            'testimonials': testimonials,
            'services': services_list,  # Changed from 'services_list' to 'services'
            'supporting_services': supporting_services,
            'featured_projects': featured_projects,
            'result_stats': result_stats,
            'categories': categories,
        }
        return render(request, 'AI_tech/home.html', context)
    except Exception as e:
        # Fallback if database is empty
        context = {
            'testimonials': [],
            'services': [],
            'supporting_services': [],
            'featured_projects': [],
            'result_stats': [],
            'categories': [],
        }
        return render(request, 'AI_tech/home.html', context)

def services(request):
    # For form submission handling
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            company_name = request.POST.get('company')
            description = request.POST.get('message')
            phone = request.POST.get('phone')
            
            ServiceConsultation.objects.create(
                name=name,
                email=email,
                company_name=company_name,
                description=description,
                phone=phone
            )
            
            messages.success(request, 'Thank you! Your consultation request has been submitted successfully.')
            return redirect('services')
            
        except Exception as e:
            messages.error(request, 'There was an error submitting your request. Please try again.')
    
    # For GET request
    services_list = Service.objects.filter(status=True)
    supporting_services = SupportingService.objects.filter(status=True)
    
    context = {
        'services': services_list,
        'supporting_services': supporting_services,
    }
    return render(request, 'AI_tech/services.html', context)

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, status=True)
    related_services = Service.objects.filter(status=True).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'AI_tech/service_detail.html', context)

def portfolio(request):
    portfolio_projects = PortfolioProject.objects.filter(is_active=True).select_related('category')
    result_stats = ResultStatistic.objects.filter(is_active=True, status=True)
    categories = ProjectCategory.objects.filter(is_active=True)
    
    context = {
        'portfolio_projects': portfolio_projects,
        'result_stats': result_stats,
        'categories': categories,
    }
    return render(request, 'AI_tech/portfolio.html', context)

def portfolio_detail(request, pk):
    project = get_object_or_404(PortfolioProject, id=pk, is_active=True)
    related_projects = PortfolioProject.objects.filter(
        is_active=True, 
        category=project.category
    ).exclude(id=project.id)[:2]
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'AI_tech/portfolio_detail.html', context)


def aboutus(request):
    result_stats = ResultStatistic.objects.filter(is_active=True, status=True).order_by('order')[:4]
    return render(request, 'AI_tech/aboutus.html', {'result_stats': result_stats})


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



from django.views.generic import ListView, DetailView

class ServiceListView(ListView):
    model = Service
    template_name = 'AI_tech/services.html'
    context_object_name = 'services_list'
    
    def get_queryset(self):
        return Service.objects.filter(status=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supporting_services'] = SupportingService.objects.filter(status=True)
        return context

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'AI_tech/service_detail.html'
    context_object_name = 'service'
    def get_queryset(self):
        return Service.objects.filter(status=True)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['features'] = self.object.get_features()
        return context


def project_gallery(request):
    images = ProjectImage.objects.filter(
        project__is_active=True, 
        status=True
    ).select_related('project').order_by('project__order', 'order')
    
    context = {
        'images': images,
    }
    return render(request, 'AI_tech/home.html', context)


def project_images(request, pk):
    project = get_object_or_404(PortfolioProject, id=pk, is_active=True)
    images = ProjectImage.objects.filter(project=project)
    
    context = {
        'project': project,
        'images': images,
    }
    return render(request, 'AI_tech/home.html', context)

from django.http import JsonResponse
import json

# AJAX endpoint for project images
def project_images_ajax(request, pk):
    project = get_object_or_404(PortfolioProject, id=pk, is_active=True)
    images = ProjectImage.objects.filter(project=project, status=True)
    
    images_data = []
    for image in images:
        images_data.append({
            'id': image.id,
            'title': image.title or image.project.title,
            'description': image.description or '',
            'url': request.build_absolute_uri(image.image.url) if image.image else '',
        })
    
    return JsonResponse({
        'success': True,
        'project_id': pk,
        'project_title': project.title,
        'images': images_data
    })

# AJAX endpoint for gallery
def project_gallery_ajax(request):
    images = ProjectImage.objects.filter(
        project__is_active=True, 
        status=True
    ).select_related('project').order_by('project__order', 'order')[:50]
    
    images_data = []
    for image in images:
        images_data.append({
            'id': image.id,
            'title': image.title or image.project.title,
            'description': image.description or '',
            'url': request.build_absolute_uri(image.image.url) if image.image else '',
            'project_title': image.project.title,
            'project_id': image.project.id,
        })
    
    return JsonResponse({
        'success': True,
        'count': len(images_data),
        'images': images_data
    })



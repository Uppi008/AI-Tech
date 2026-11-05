from django.db import models
from datetime import datetime
from django.forms import ValidationError
from django.utils import timezone

from aitech.validators import alphanumeric, validate_Email, validate_phone_number

class ConsoleAdminDetails(models.Model):
    console_full_name = models.CharField(max_length=200, null=True)
    console_image = models.ImageField(upload_to="Console_Image", null=True, blank=True)
    console_email = models.EmailField(null=True, unique=True)  # Added unique=True
    console_phone_number = models.CharField(max_length=200, null=True, blank=True)
    console_password = models.CharField(max_length=255, default='default_password')
    status = models.BooleanField(default=True)  # Changed default to True for auto-activation
    created_at = models.DateTimeField(default=datetime.now)
    
    class Meta:
        verbose_name = "Console Admin"
        verbose_name_plural = "Console Admins"
    
    def __str__(self):
        return self.console_full_name or self.console_email
    
    def clean(self):
        # Validate fields on model save
        if self.console_full_name:
            self.console_full_name = alphanumeric(self.console_full_name)
        
        if self.console_email:
            self.console_email = validate_Email(self.console_email)
        
        if self.console_phone_number:
            self.console_phone_number = validate_phone_number(self.console_phone_number)
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)
# -----------------------
# Contact Information
# -----------------------
class ContactInfo(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    company_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.TextField()
    location = models.CharField(max_length=200, help_text="City, State, Country")
    map_link = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name


# -----------------------
# Contact Messages
# -----------------------
class ContactMessage(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Message from {self.name}"


# -----------------------
# Services
# -----------------------
# class Service(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     icon = models.CharField(max_length=100, help_text="Use FontAwesome icon class, e.g., fa-robot")
#     slug = models.SlugField(unique=True)
#     created_date = models.DateTimeField(auto_now_add=True)
#     status = models.BooleanField(default=True)

#     def __str__(self):
#         return self.title
    


class Service(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="Use FontAwesome icon class, e.g., fa-robot")
    slug = models.SlugField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)
    
    # New fields based on your services section
    category = models.CharField(max_length=100, help_text="e.g., Predictive Analytics, Text Intelligence")
    short_description = models.TextField(blank=True, help_text="Short description for cards")
    
    # Background image for the service card
    background_image = models.ImageField(upload_to='services/bg_images/', blank=True, null=True)
    
    # Gradient colors for the service
    gradient_start = models.CharField(max_length=7, default='#4361ee', help_text="Hex color code for gradient start")
    gradient_end = models.CharField(max_length=7, default='#3a0ca3', help_text="Hex color code for gradient end")
    
    # Badge color
    badge_color = models.CharField(max_length=7, default='#4cc9f0', help_text="Hex color code for badge")
    
    def __str__(self):
        return self.title
    
    def get_features(self):
        return self.features.all()
    
    class Meta:
        ordering = ['created_date']
        
class ServiceFeature(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.service.title} - {self.name}"
    
    class Meta:
        ordering = ['order']

class SupportingService(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="Use FontAwesome icon class")
    badge_text = models.CharField(max_length=50, help_text="e.g., Planning, Deployment")
    gradient_start = models.CharField(max_length=7, default='#4361ee')
    gradient_end = models.CharField(max_length=7, default='#3a0ca3')
    badge_color = models.CharField(max_length=7, default='#4361ee')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        verbose_name = "Supporting Service"
        verbose_name_plural = "Supporting Services"


# -----------------------
# Service Consultation
# -----------------------
class ServiceConsultation(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company_name = models.CharField(max_length=100)
    description = models.TextField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Consultation by {self.name}"


# -----------------------
# Testimonials
# -----------------------
class Testimonial(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, help_text="e.g., CEO, Marketing Director, etc.")
    company = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField(help_text="The testimonial content")
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5, help_text="Rating from 1 to 5 stars")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.name} - {self.role}"


# -----------------------
# Project Category
# -----------------------
class ProjectCategory(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class, e.g., fas fa-brain")
    color = models.CharField(max_length=7, default='#1976d2', help_text="Hex color code for the category")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Project Category'
        verbose_name_plural = 'Project Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


# -----------------------
# Portfolio Projects
# -----------------------
class PortfolioProject(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='portfolio/')
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='projects')
    client = models.CharField(max_length=200, blank=True)
    project_date = models.DateField()
    technologies = models.CharField(max_length=300, help_text="Comma-separated list of technologies used")
    
    # Optional metadata fields
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers show first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-project_date']
        verbose_name = 'Portfolio Project'
        verbose_name_plural = 'Portfolio Projects'

    def __str__(self):
        return self.title

    def get_technologies_list(self):
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]

# -----------------------
# Project Images
# -----------------------
class ProjectImage(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(PortfolioProject, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='portfolio/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"


# -----------------------
# Result Statistics
# -----------------------
class ResultStatistic(models.Model):
    console_full_name = models.ForeignKey(ConsoleAdminDetails, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    value = models.CharField(max_length=100, help_text="e.g., 45%, $3.2M, 68%")
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class, e.g., fas fa-chart-line")
    order = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Result Statistic'
        verbose_name_plural = 'Result Statistics'

    def __str__(self):
        return self.title

from django.db import models

# Create your models here.
class ContactInfo(models.Model):
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

    def __str__(self):
        return self.company_name

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Message from {self.name}"
    
class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="Use FontAwesome icon class, e.g., fa-robot")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
    
class ServiceConsultation(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company_name = models.CharField(max_length=100)
    description = models.TextField()
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Service from {self.name}"
    
class Testimonial(models.Model):
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
    

class ProjectCategory(models.Model):
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

class PortfolioProject(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='portfolio/')
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='projects')
    client = models.CharField(max_length=200, blank=True)
    project_date = models.DateField()
    project_url = models.URLField(blank=True, null=True)
    technologies = models.CharField(max_length=300, help_text="Comma-separated list of technologies used")
    challenge = models.TextField(blank=True, help_text="The business challenge faced")
    solution = models.TextField(blank=True, help_text="The AI solution implemented")
    results = models.TextField(blank=True, help_text="The results achieved")
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
        return [tech.strip() for tech in self.technologies.split(',')]

class ProjectImage(models.Model):
    project = models.ForeignKey(PortfolioProject, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='portfolio/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"

class ResultStatistic(models.Model):
    title = models.CharField(max_length=200)
    value = models.CharField(max_length=100, help_text="e.g., 45%, $3.2M, 68%")
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class, e.g., fas fa-chart-line")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Result Statistic'
        verbose_name_plural = 'Result Statistics'

    def __str__(self):
        return self.title
from django.contrib import admin

# Register your models here.
from .models import *
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'slug')
    prepopulated_fields = {"slug": ("title",)}
    
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceConsultation)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(ContactMessage)
admin.site.register(Testimonial)
admin.site.register(ProjectCategory)
admin.site.register(PortfolioProject)
admin.site.register(ProjectImage)
admin.site.register(ResultStatistic)

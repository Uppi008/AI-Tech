from django.contrib import admin

# Register your models here.
from .models import *
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone')


admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(ContactMessage)
admin.site.register(Testimonial)
admin.site.register(ProjectCategory)
admin.site.register(PortfolioProject)
admin.site.register(ProjectImage)
admin.site.register(ResultStatistic)


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1





class ServiceFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'order']
    list_filter = ['service']
    search_fields = ['name', 'service__title']


class SupportingServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'badge_text', 'order', 'status']
    list_filter = ['status']
    search_fields = ['title', 'description']

admin.site.register(Service)
admin.site.register(ServiceConsultation)
admin.site.register(ServiceFeature,ServiceFeatureAdmin)
admin.site.register(SupportingService,SupportingServiceAdmin)
admin.site.register(ConsoleAdminDetails)
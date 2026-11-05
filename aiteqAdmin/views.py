from django.shortcuts import render, get_object_or_404,redirect
from aitech.models import *
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import csv  
from datetime import datetime
from django.utils.dateparse import parse_date
from aitech.utils import decrypt_id
from aitech.validators import alphanumeric, validate_Email, validate_phone_number
from functools import wraps
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
import re



# ===================== DECORATOR =====================
def console_login_required(view_function):
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, 'Please login to access this page.')
            return redirect('console_signin')
        return view_function(request, *args, **kwargs)
    return wrapper


# ===================== VIEW FUNCTIONS =====================
def console_auth(request):
    """Handle both login and signup"""
    # If already logged in, redirect to dashboard
    if request.session.get('user_id'):
        return redirect('dashboard')
    
    # Initialize context with default values
    context = {
        'show_signup': False,
        'form_data': {}
    }
    
    if request.method == 'POST':
        action = request.POST.get('action', 'login')
        
        if action == 'login':
            # ================= LOGIN =================
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            
            # Store form data for re-display
            context['form_data'] = {'email': email}
            
            # Validate inputs
            if not email or not password:
                messages.error(request, "Please provide both email and password.")
                return render(request, 'Authentication/login/login.html', context)
            
            try:
                # Try to get user - check with lowercase email
                user = ConsoleAdminDetails.objects.get(console_email=email)
                
                # Check if account is active
                if not user.status:
                    messages.error(request, "Your account is inactive. Please contact administrator.")
                    return render(request, 'Authentication/login/login.html', context)
                
                # Verify password
                if check_password(password, user.console_password):
                    # Set session variables
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.console_full_name
                    request.session['user_email'] = user.console_email
                    request.session.set_expiry(3600)  # Session expires in 1 hour
                    
                    messages.success(request, f"Welcome back, {user.console_full_name}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
            
            except ConsoleAdminDetails.DoesNotExist:
                messages.error(request, "No account found with this email.")
            except Exception as e:
                messages.error(request, f"Login error: {str(e)}")
        
        elif action == 'signup':
            # ================= SIGNUP =================
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip().lower()
            phone = request.POST.get('phone', '').strip()
            password = request.POST.get('password', '')
            
            # Store form data for re-display
            context['form_data'] = {
                'name': name,
                'email': email,
                'phone': phone,
            }
            context['show_signup'] = True
            
            # Validate inputs
            errors = []
            
            # Validate name
            try:
                name = alphanumeric(name)
            except ValidationError as e:
                errors.append(str(e))
            
            # Validate email
            try:
                email = validate_Email(email)
            except ValidationError as e:
                errors.append(str(e))
            
            # Validate phone
            try:
                phone = validate_phone_number(phone)
            except ValidationError as e:
                errors.append(str(e))
            
            # Validate password
            if len(password) < 6:
                errors.append("Password must be at least 6 characters long.")
            
            # Check if email already exists (case-insensitive)
            if ConsoleAdminDetails.objects.filter(console_email__iexact=email).exists():
                errors.append("This email is already registered.")
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'Authentication/login/login.html', context)
            
            try:
                # Create new user - use make_password() to hash the password
                user = ConsoleAdminDetails.objects.create(
                    console_full_name=name,
                    console_email=email,
                    console_phone_number=phone,
                    console_password=make_password(password),  # FIXED: Hashing the password
                    status=True  # Auto-activate account on signup
                )
                
                messages.success(request, "Account created successfully! Please login.")
                # Clear form data and show login form on success
                context['form_data'] = {}
                context['show_signup'] = False
                return render(request, 'Authentication/login/login.html', context)
            
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return render(request, 'Authentication/login/login.html', context)
    
    # GET request - render login page
    else:
        # Check if user clicked signup tab
        if request.GET.get('action') == 'signup':
            context['show_signup'] = True
    
    return render(request, 'Authentication/login/login.html', context)


def console_logout(request):
    """Handle logout"""
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('console_signin')


# ===================== DASHBOARD VIEW =====================
@console_login_required
def dashboard(request):
    """Dashboard view - requires login"""
    user_id = request.session.get('user_id')
    try:
        user = ConsoleAdminDetails.objects.get(id=user_id)
        context = {
            'user_name': user.console_full_name,
            'user_email': user.console_email,
        }
        return render(request, 'Dashboard/dashboard.html', context)
    except ConsoleAdminDetails.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('console_signin')

def base(request):
    return render(request, 'aiteq/base_admin.html')

def General_Settings(request):
    return render(request, 'General_settings/settings.html')


@console_login_required
def contact_info_edit(request):
    contact_info = ContactInfo.objects.first()
    if not contact_info:
        contact_info = ContactInfo.objects.create(
            company_name="Your Company", phone="", email="", address="", location=""
        )

    if request.method == 'POST':
        try:
            company_name = request.POST.get('company_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            address = request.POST.get('address', '').strip()
            location = request.POST.get('location', '').strip()
            map_link = request.POST.get('map_link', '').strip()
            facebook = request.POST.get('facebook', '').strip()
            linkedin = request.POST.get('linkedin', '').strip()
            twitter = request.POST.get('twitter', '').strip()
            instagram = request.POST.get('instagram', '').strip()

            errors = []
            if not company_name:
                errors.append("Company name is required.")
            if not phone:
                errors.append("Phone number is required.")
            elif not re.match(r'^[0-9+\-\s()]{7,20}$', phone):
                errors.append("Please enter a valid phone number.")

            if not email:
                errors.append("Email is required.")
            else:
                try:
                    email = validate_Email(email)
                except ValidationError as e:
                    errors.append(str(e))

            if not address:
                errors.append("Address is required.")
            if not location:
                errors.append("Location is required.")

            for url_field, label in (
                (map_link, "Map link"), (facebook, "Facebook URL"),
                (linkedin, "LinkedIn URL"), (twitter, "Twitter URL"), (instagram, "Instagram URL"),
            ):
                if url_field and not re.match(r'^https?://', url_field):
                    errors.append(f"{label} must start with http:// or https://.")

            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('contact_info_edit')

            contact_info.company_name = company_name
            contact_info.phone = phone
            contact_info.email = email
            contact_info.address = address
            contact_info.location = location
            contact_info.map_link = map_link
            contact_info.facebook = facebook
            contact_info.linkedin = linkedin
            contact_info.twitter = twitter
            contact_info.instagram = instagram
            contact_info.save()

            messages.success(request, "Contact info updated successfully!")
            return redirect('contact_info_edit')

        except Exception as e:
            messages.error(request, f"Error updating contact info: {str(e)}")
            return redirect('contact_info_edit')

    return render(
        request,
        'General_settings/general_setting_page/ContactInfo/contact_info_edit.html',
        {'contact_info': contact_info}
    )


@console_login_required
def service_list(request):
    if request.method == "POST":
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            short_description = request.POST.get('short_description')
            category = request.POST.get('category')
            icon = request.POST.get('icon')
            status = request.POST.get('status') == 'on'

            gradient_start = request.POST.get('gradient_start', '#4361ee')
            gradient_end = request.POST.get('gradient_end', '#3a0ca3')
            badge_color = request.POST.get('badge_color', '#4cc9f0')

            background_image = request.FILES.get('background_image')

          
            if not title:
                messages.error(request, "Service title is required.")
                return redirect('service_list')

            if Service.objects.filter(title__iexact=title).exists():
                messages.error(request, f"Service '{title}' already exists.")
                return redirect('service_list')

           
            # user_id = request.session.get('user_id')
            # if not user_id:
            #     messages.error(request, "User not authenticated. Please login again.")
            #     return redirect('login')

            # try:
            #     console_admin = ConsoleAdminDetails.objects.get(id=user_id)
            # except ConsoleAdminDetails.DoesNotExist:
            #     messages.error(request, "Admin user not found.")
            #     return redirect('login')

           
            base_slug = slugify(title)
            slug = base_slug
            count = 1
            while Service.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

        
            Service.objects.create(
                # console_full_name=console_admin,
                title=title,
                description=description,
                short_description=short_description,
                category=category,
                icon=icon,
                slug=slug,
                status=status,
                background_image=background_image,
                gradient_start=gradient_start,
                gradient_end=gradient_end,
                badge_color=badge_color
            )

            messages.success(request, f"Service '{title}' created successfully!")
            return redirect('service_list')

        except Exception as e:
            messages.error(request, f"Error creating service: {str(e)}")
            return redirect('service_list')

    return render(
        request,
        'General_settings/general_setting_page/Services/services_list.html'
    )

@console_login_required
def get_details_service(request):
    if request.headers.get("HX-Request"):
        search = request.GET.get("search")
        get_edit = request.GET.get("get_edit")
        get_delete = request.GET.get("get_delete")
        get_view = request.GET.get("get_view")
        page_number = request.GET.get("page", 1)
        
        if get_view:
                service = get_object_or_404(Service, id=get_view)
                return render(request, "General_settings/general_setting_page/Services/Service_com/service_view.html", {
                    "service": service
                })
        
        if get_edit:
            service = get_object_or_404(Service, id=get_edit)
            return render(
                request,
                "General_settings/general_setting_page/Services/Service_com/service_edit.html",
                {"service": service}
            )

        if get_delete:
            service = get_object_or_404(Service, id=get_delete)
            return render(
                request,
                "General_settings/general_setting_page/Services/Service_com/service_delete.html",
                {"service": service}
            )

        query = Q()
        if search:
            query &= Q(title__icontains=search) | Q(
                category__icontains=search
            )

        service = Service.objects.filter(query).order_by("-created_date")

        paginator = Paginator(service, 10)
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            "General_settings/general_setting_page/Services/Service_com/service_table.html",
            {"service": page_obj, "page_obj": page_obj},
        )

@console_login_required
def update_service(request, id):
    service_id = id
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            category = request.POST.get('category', '').strip()
            icon = request.POST.get('icon', '').strip()

            status = request.POST.get('u_status') == 'on'

            gradient_start = request.POST.get('gradient_start') or '#4361ee'
            gradient_end = request.POST.get('gradient_end') or '#3a0ca3'
            badge_color = request.POST.get('badge_color') or '#4cc9f0'

            background_image = request.FILES.get('background_image')

            # Validation
            if not title:
                messages.error(request, "Service title is required.")
                return redirect('service_list')

            if Service.objects.filter(title__iexact=title).exclude(id=service_id).exists():
                messages.error(request, f"Service '{title}' already exists.")
                return redirect('service_list')

            # Slug
            base_slug = slugify(title)
            slug = base_slug
            count = 1
            while Service.objects.filter(slug=slug).exclude(id=service_id).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            # Admin assign
            # user_id = request.session.get('user_id')
            # if user_id:
            #     try:
            #         service.console_full_name = ConsoleAdminDetails.objects.get(id=user_id)
            #     except ConsoleAdminDetails.DoesNotExist:
            #         pass

            # Update
            service.title = title
            service.slug = slug
            service.description = description
            service.short_description = short_description
            service.category = category
            service.icon = icon
            service.status = status
            service.gradient_start = gradient_start
            service.gradient_end = gradient_end
            service.badge_color = badge_color

            if background_image:
                service.background_image = background_image

            service.save()

            messages.success(request, f"Service '{title}' updated successfully!")
            return redirect('service_list')

        except Exception as e:
            messages.error(request, f"Error updating service: {str(e)}")
            return redirect('service_list')

    if request.headers.get('HX-Request'):
       service = Service.objects.all()
       return render(request, 'General_settings/general_setting_page/Services/Service_com/service_table.html', {
        'service': service
    })

@console_login_required
def delete_service(request, id): 
  
    service_id = id
    
    try:
        service = get_object_or_404(Service, id=service_id)

        if request.method == "POST":
            title = service.title
            service.delete()
            messages.success(request, f"Service '{title}' deleted successfully!")
            return redirect('service_list')

    except Exception as e:
        messages.error(request, f"Error deleting service: {str(e)}")
        return redirect('service_list')

@console_login_required
def toggle_service_status(request, service_id):
    try:
        service = get_object_or_404(Service, id=service_id)

        # Toggle status
        service.status = not service.status
        service.save()

        status_text = "Active" if service.status else "Deactive"
        badge_class = "bg-success" if service.status else "bg-danger"

        url = reverse("toggle_service_status", args=[service.id])

        return HttpResponse(
            f'<span hx-get="{url}" '
            f'hx-target="this" hx-swap="outerHTML" '
            f'class="badge {badge_class}" style="cursor:pointer;">'
            f'{status_text}</span>'
        )

    except Service.DoesNotExist:
        raise Http404("Service not found.")

    except Exception:
        return HttpResponse(
            '<span class="badge bg-warning text-dark" style="cursor:not-allowed;">Error</span>'
        )

@console_login_required
def get_service_report(request):
    try:
        if request.method == "POST":
            start_date_str = request.POST.get('service_startdatereport')
            end_date_str = request.POST.get('service_enddatereport')
            export_file_type = request.POST.get('export_file_type')

            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)

            formatted_start = start_date.strftime('%d-%m-%Y')
            formatted_end = end_date.strftime('%d-%m-%Y')

            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())

            service_list = Service.objects.filter(
                created_date__range=(start_datetime, end_datetime)
            ).order_by("-created_date")

         
            if export_file_type == 'PDF':
                context = {
                    'service_list': service_list,
                    'service_startdatereport': formatted_start,
                    'service_enddatereport': formatted_end,
                }

                html = render_to_string(
                    'General_settings/general_setting_page/Services/Service_com/service_report_pdf.html',
                    context
                )

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = (
                    f'inline; filename="service_report_{datetime.now().date()}.pdf"'
                )

                from xhtml2pdf import pisa
                pisa_status = pisa.CreatePDF(html, dest=response)

                if pisa_status.err:
                    messages.error(request, 'Error generating PDF.', extra_tags='danger')
                    return redirect('service_list')

                return response

    
            elif export_file_type == 'CSV':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = (
                    f'attachment; filename="service_report_{datetime.now().strftime("%Y%m%d")}.csv"'
                )

                writer = csv.writer(response)
                writer.writerow(['S.No', 'Title', 'Category', 'Status', 'Created At'])

                for index, item in enumerate(service_list, start=1):
                    status = "Active" if item.status else "Deactive"
                    writer.writerow([
                        index,
                        item.title,
                        item.category,
                        status,
                        item.created_date.strftime('%d-%m-%Y')
                    ])

                return response

            else:
                messages.error(request, 'Invalid export type.', extra_tags='danger')
                return redirect('service_list')

        messages.error(request, 'Invalid request.', extra_tags='danger')
        return redirect('service_list')

    except Exception as e:
        messages.error(request, f"Error: {str(e)}", extra_tags='danger')
        return redirect('service_list')

@console_login_required
def bulk_upload_service(request):
    try:
        if request.method == "POST":
            csv_file = request.FILES.get('file')

            if not csv_file:
                messages.error(request, 'No file uploaded.', extra_tags='danger')
                return redirect('service_list')

            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.', extra_tags='danger')
                return redirect('service_list')

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            next(reader, None)  # Skip header

            imported_count = duplicate_count = invalid_count = 0
            row_number = 1

            for row in reader:
                row_number += 1

                if not row or all(cell.strip() == '' for cell in row):
                    continue

                if len(row) < 3:
                    invalid_count += 1
                    continue

                title = row[1].strip()
                category = row[2].strip()

                status = True
                if len(row) > 3:
                    status = row[3].strip().lower() == 'active'

                if not title or not category:
                    invalid_count += 1
                    continue

                if Service.objects.filter(title__iexact=title).exists():
                    duplicate_count += 1
                    continue

                slug = slugify(title)
                count = 1
                while Service.objects.filter(slug=slug).exists():
                    slug = f"{slugify(title)}-{count}"
                    count += 1

                Service.objects.create(
                    title=title,
                    category=category,
                    slug=slug,
                    status=status,
                    description="",
                    short_description=""
                )

                imported_count += 1

            if imported_count:
                messages.success(request, f"{imported_count} services imported successfully.")
            if duplicate_count:
                messages.warning(request, f"{duplicate_count} duplicate services skipped.")
            if invalid_count:
                messages.error(request, f"{invalid_count} invalid rows skipped.", extra_tags='danger')

            return redirect('service_list')

    except Exception as e:
        messages.error(request, f"Unexpected error: {str(e)}", extra_tags='danger')
        return redirect('service_list')

@console_login_required
def supporting_service_list(request):
    if request.method == "POST":
        try:
            # Get form data
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            icon = request.POST.get('icon', '').strip()
            badge_text = request.POST.get('badge_text', '').strip()
            gradient_start = request.POST.get('gradient_start', '#4361ee')
            gradient_end = request.POST.get('gradient_end', '#3a0ca3')
            badge_color = request.POST.get('badge_color', '#4361ee')
            order = request.POST.get('order', 0)
            status = request.POST.get('status', 'on') == 'on'

            # Basic validation
            if not title:
                messages.error(request, "Service title is required.")
                return redirect('supporting_service_list')

            if not description:
                messages.error(request, "Service description is required.")
                return redirect('supporting_service_list')

            if not icon:
                messages.error(request, "Icon class is required.")
                return redirect('supporting_service_list')

            # Duplicate check (case-insensitive)
            if SupportingService.objects.filter(title__iexact=title).exists():
                messages.error(
                    request,
                    f"A supporting service with the title '{title}' already exists."
                )
                return redirect('supporting_service_list')

            # Get logged-in admin from session
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, "User not authenticated. Please login again.")
                return redirect('login')

            try:
                console_admin = ConsoleAdminDetails.objects.get(id=user_id)
            except ConsoleAdminDetails.DoesNotExist:
                messages.error(request, "Admin user not found.")
                return redirect('login')

            # Create Supporting Service
            SupportingService.objects.create(
                console_full_name=console_admin,
                title=title,
                description=description,
                icon=icon,
                badge_text=badge_text,
                gradient_start=gradient_start,
                gradient_end=gradient_end,
                badge_color=badge_color,
                order=int(order),
                status=status
            )

            messages.success(request, f"Supporting service '{title}' created successfully!")
            return redirect('supporting_service_list')

        except Exception as e:
            messages.error(request, f"Error creating supporting service: {str(e)}")
            return redirect('supporting_service_list')

    # GET request
    services = SupportingService.objects.all()
    return render(
        request,
        'General_settings/general_setting_page/Supporting_Service/supporting_Service_list.html',
        {'services': services}
    )
    
@console_login_required
def get_details_supporting_service(request):
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('search')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')

            if get_edit:
                service = get_object_or_404(SupportingService, id=get_edit)
                return render(
                    request,
                    'General_settings/general_setting_page/Supporting_Service/components/supporting_service_edit.html',
                    {'service': service}
                )

            if get_delete:
                service = get_object_or_404(SupportingService, id=get_delete)
                return render(
                    request,
                    'General_settings/general_setting_page/Supporting_Service/components/supporting_service_delete.html',
                    {'service': service}
                )

            query = Q()
            if search:
                query = Q(title__icontains=search)

            services = SupportingService.objects.filter(query)
            paginator = Paginator(services, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            return render(
                request,
                'General_settings/general_setting_page/Supporting_Service/components/supporting_service_table.html',
                {'services': page_obj}
            )

        except Exception as e:
            return HttpResponse(f"Error loading data: {str(e)}", status=500)

@console_login_required
def update_supporting_service(request, id):
    service_id = id

    if request.method == 'POST':
        try:
            service = get_object_or_404(SupportingService, id=service_id)

            title = request.POST.get('u_title', '').strip()
            description = request.POST.get('u_description', '').strip()
            icon = request.POST.get('u_icon', '').strip()
            badge_text = request.POST.get('u_badge_text', '').strip()
            gradient_start = request.POST.get('u_gradient_start', '#4361ee')
            gradient_end = request.POST.get('u_gradient_end', '#3a0ca3')
            badge_color = request.POST.get('u_badge_color', '#4361ee')
            order = request.POST.get('u_order', 0)

            if not title:
                messages.error(request, "Service title is required.")
                return redirect('supporting_service_list')

            if SupportingService.objects.filter(
                title__iexact=title
            ).exclude(id=service_id).exists():
                messages.error(request, f"Service '{title}' already exists.")
                return redirect('supporting_service_list')

            user_id = request.session.get('user_id')
            if user_id:
                try:
                    service.console_full_name = ConsoleAdminDetails.objects.get(id=user_id)
                except ConsoleAdminDetails.DoesNotExist:
                    pass

            service.title = title
            service.description = description
            service.icon = icon
            service.badge_text = badge_text
            service.gradient_start = gradient_start
            service.gradient_end = gradient_end
            service.badge_color = badge_color
            service.order = int(order)
            service.save()

            messages.success(request, f"Service '{title}' updated successfully!")
            return redirect('supporting_service_list')

        except Exception as e:
            messages.error(request, f"Error updating service: {str(e)}")
            return redirect('supporting_service_list')


@console_login_required
def delete_supporting_service(request, id):
    service_id = id

    try:
        service = get_object_or_404(SupportingService, id=service_id)

        if request.method == "POST":
            service.delete()
            messages.success(request, f"Service '{service.title}' deleted successfully!")
            return redirect('supporting_service_list')

    except Exception as e:
        messages.error(request, f"Error deleting service: {str(e)}")
        return redirect('supporting_service_list')


@console_login_required
def toggle_supporting_service_status(request, service_id):
    try:
        service = get_object_or_404(SupportingService, id=service_id)
        service.status = not service.status
        service.save()

        status_text = "Active" if service.status else "Inactive"
        badge_class = "bg-success" if service.status else "bg-danger"

        url = reverse("toggle_supporting_service_status", args=[service.id])

        return HttpResponse(
            f'<span hx-get="{url}" hx-target="this" hx-swap="outerHTML" '
            f'class="badge {badge_class}" style="cursor:pointer;">'
            f'{status_text}</span>'
        )

    except Exception:
        return HttpResponse(
            '<span class="badge bg-warning text-dark">Error</span>'
        )

@console_login_required
def get_supporting_service_report(request):
    try:
        if request.method == "POST":
            start_date = parse_date(request.POST.get('start_date'))
            end_date = parse_date(request.POST.get('end_date'))
            export_type = request.POST.get('export_file_type')

            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())

            services = SupportingService.objects.filter(
                created_at__range=(start_dt, end_dt)
            )

            if export_type == "CSV":
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="supporting_services.csv"'
                writer = csv.writer(response)

                writer.writerow(['S.No', 'Title', 'Status'])
                for i, s in enumerate(services, 1):
                    writer.writerow([i, s.title, "Active" if s.status else "Inactive"])

                return response

        messages.error(request, "Invalid request")
        return redirect('supporting_service_list')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('supporting_service_list')

@console_login_required
def bulk_upload_supporting_service(request):
    try:
        if request.method == "POST":
            csv_file = request.FILES.get('file')

            if not csv_file or not csv_file.name.endswith('.csv'):
                messages.error(request, "Upload a valid CSV file.")
                return redirect('supporting_service_list')

            decoded = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded)
            next(reader, None)

            imported = duplicates = 0

            for row in reader:
                if len(row) < 2:
                    continue

                title = row[1].strip()
                if not title:
                    continue

                if SupportingService.objects.filter(title__iexact=title).exists():
                    duplicates += 1
                    continue

                SupportingService.objects.create(
                    title=title,
                    description="",
                    icon="fa-solid fa-cogs",
                    badge_text="General"
                )
                imported += 1

            messages.success(request, f"{imported} services imported.")
            if duplicates:
                messages.warning(request, f"{duplicates} duplicates skipped.")

            return redirect('supporting_service_list')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('supporting_service_list')



@console_login_required
def service_consultation_list(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            company_name = request.POST.get('company_name', '').strip()
            description = request.POST.get('description', '').strip()
            phone = request.POST.get('phone', '').strip()

            # Basic validation
            if not name or not email or not company_name or not description:
                messages.error(request, "All required fields must be filled.")
                return redirect('service_consultation_list')

            # Get logged-in admin from session
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, "User not authenticated. Please login again.")
                return redirect('login')  # adjust if needed

            try:
                console_admin = ConsoleAdminDetails.objects.get(id=user_id)
            except ConsoleAdminDetails.DoesNotExist:
                messages.error(request, "Admin user not found.")
                return redirect('login')

            # Create Service Consultation
            ServiceConsultation.objects.create(
                console_full_name=console_admin,
                name=name,
                email=email,
                company_name=company_name,
                description=description,
                phone=phone if phone else None
            )

            messages.success(request, "Service consultation created successfully!")
            return redirect('service_consultation_list')

        except Exception as e:
            messages.error(request, f"Error creating service consultation: {str(e)}")
            return redirect('service_consultation_list')

    return render(
        request,
        'General_settings/general_setting_page/Service_Consultation/service_consultation_list.html'
    )


@console_login_required
def get_details_service_consultation(request):
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('search')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')

            # Edit modal
            if get_edit:
                consultation = get_object_or_404(ServiceConsultation, id=get_edit)
                return render(
                    request,
                    'General_settings/general_setting_page/Service_Consultation/components/service_consultation_edit.html',
                    {'consultation': consultation}
                )

            # Delete modal
            if get_delete:
                consultation = get_object_or_404(ServiceConsultation, id=get_delete)
                return render(
                    request,
                    'General_settings/general_setting_page/Service_Consultation/components/service_consultation_delete.html',
                    {'consultation': consultation}
                )

            # Search
            query = Q()
            if search:
                query = (
                    Q(name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(company_name__icontains=search)
                )

            consultations = ServiceConsultation.objects.filter(query).order_by('-created_date')

            paginator = Paginator(consultations, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            return render(
                request,
                'General_settings/general_setting_page/Service_Consultation/components/service_consultation_table.html',
                {'consultations': page_obj}
            )

        except Exception as e:
            return HttpResponse(f"Error loading data: {str(e)}", status=500)

@console_login_required
def update_service_consultation(request, id):
    consultation_id = id
    if request.method == 'POST':
        try:
            consultation = get_object_or_404(ServiceConsultation, id=consultation_id)

            name = request.POST.get('u_name', '').strip()
            email = request.POST.get('u_email', '').strip()
            company_name = request.POST.get('u_company_name', '').strip()
            description = request.POST.get('u_description', '').strip()
            phone = request.POST.get('u_phone', '').strip()

            if not name or not email or not company_name or not description:
                messages.error(request, "All required fields are mandatory.")
                return redirect('service_consultation_list')

            # Update admin (optional tracking)
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    consultation.console_full_name = ConsoleAdminDetails.objects.get(id=user_id)
                except ConsoleAdminDetails.DoesNotExist:
                    pass

            consultation.name = name
            consultation.email = email
            consultation.company_name = company_name
            consultation.description = description
            consultation.phone = phone if phone else None
            consultation.save()

            messages.success(request, "Service consultation updated successfully!")
            return redirect('service_consultation_list')

        except Exception as e:
            messages.error(request, f"Error updating consultation: {str(e)}")
            return redirect('service_consultation_list')

@console_login_required
def delete_service_consultation(request, id):
    consultation_id = id

    try:
        consultation = get_object_or_404(ServiceConsultation, id=consultation_id)

        if request.method == "POST":
            consultation.delete()
            messages.success(
                request,
                f"Consultation by '{consultation.name}' deleted successfully!"
            )
            return redirect('service_consultation_list')

    except Exception as e:
        messages.error(request, f"Error deleting consultation: {str(e)}")
        return redirect('service_consultation_list')

@console_login_required
def toggle_service_consultation_status(request, consultation_id):
    try:
        consultation = get_object_or_404(ServiceConsultation, id=consultation_id)

        # Toggle status
        consultation.status = not consultation.status
        consultation.save()

        status_text = "Active" if consultation.status else "Deactive"
        badge_class = "bg-success" if consultation.status else "bg-danger"

        url = reverse("toggle_service_consultation_status", args=[consultation.id])

        return HttpResponse(
            f'<span hx-get="{url}" '
            f'hx-target="this" hx-swap="outerHTML" '
            f'class="badge {badge_class}" style="cursor:pointer;">'
            f'{status_text}</span>'
        )

    except ServiceConsultation.DoesNotExist:
        raise Http404("Consultation not found")

    except Exception:
        return HttpResponse(
            '<span class="badge bg-warning text-dark">Error</span>'
        )


@console_login_required
def testimonial_list(request):
    if request.method == "POST":
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            role = request.POST.get('role', '').strip()
            company = request.POST.get('company', '').strip()
            text = request.POST.get('text', '').strip()
            rating = request.POST.get('rating', 5)
            is_active = request.POST.get('is_active') == 'on'
            image = request.FILES.get('image')

            # Validation
            if not name or not role or not text:
                messages.error(request, "Name, role, and testimonial text are required.")
                return redirect('testimonial_list')

            # Get logged-in admin from session
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, "User not authenticated. Please login again.")
                return redirect('login')

            try:
                console_admin = ConsoleAdminDetails.objects.get(id=user_id)
            except ConsoleAdminDetails.DoesNotExist:
                messages.error(request, "Admin user not found.")
                return redirect('login')

            # Create testimonial
            Testimonial.objects.create(
                console_full_name=console_admin,
                name=name,
                role=role,
                company=company,
                text=text,
                image=image,
                rating=rating,
                is_active=is_active
            )

            messages.success(request, "Testimonial added successfully!")
            return redirect('testimonial_list')

        except Exception as e:
            messages.error(request, f"Error creating testimonial: {str(e)}")
            return redirect('testimonial_list')

    return render(
        request,
        'General_settings/general_setting_page/Testimonial/testimonial_list.html'
    )
    

@console_login_required
def get_details_testimonial(request):
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('search')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')

            # -------- EDIT MODAL ----------
            if get_edit:
                testimonial = get_object_or_404(Testimonial, id=get_edit)
                return render(
                    request,
                    'General_settings/general_setting_page/Testimonial/Testimonial_com/testimonial_edit.html',
                    {'testimonial': testimonial}
                )

            # -------- DELETE MODAL ----------
            if get_delete:
                testimonial = get_object_or_404(Testimonial, id=get_delete)
                return render(
                    request,
                    'General_settings/general_setting_page/Testimonial/Testimonial_com/testimonial_delete.html',
                    {'testimonial': testimonial}
                )

            # -------- SEARCH ----------
            query = Q()
            if search:
                query = (
                    Q(name__icontains=search) |
                    Q(role__icontains=search) |
                    Q(company__icontains=search)
                )

            testimonials = Testimonial.objects.filter(query).order_by('-created_at')

            paginator = Paginator(testimonials, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            return render(
                request,
                'General_settings/general_setting_page/Testimonial/Testimonial_com/testimonial_table.html',
                {'testimonials': page_obj}
            )

        except Exception as e:
            return HttpResponse(f"Error loading data: {str(e)}", status=500)

@console_login_required
def update_testimonial(request, id):
    testimonial_id = id

    if request.method == 'POST':
        try:
            testimonial = get_object_or_404(Testimonial, id=testimonial_id)

            name = request.POST.get('u_name', '').strip()
            role = request.POST.get('u_role', '').strip()
            company = request.POST.get('u_company', '').strip()
            text = request.POST.get('u_text', '').strip()
            rating = request.POST.get('u_rating', testimonial.rating)
            image = request.FILES.get('u_image')

            if not name or not role or not text:
                messages.error(request, "Name, role, and testimonial text are required.")
                return redirect('testimonial_list')

            # Update admin reference
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    testimonial.console_full_name = ConsoleAdminDetails.objects.get(id=user_id)
                except ConsoleAdminDetails.DoesNotExist:
                    pass

            testimonial.name = name
            testimonial.role = role
            testimonial.company = company
            testimonial.text = text
            testimonial.rating = rating

            if image:
                testimonial.image = image

            testimonial.save()

            messages.success(request, "Testimonial updated successfully!")
            return redirect('testimonial_list')

        except Exception as e:
            messages.error(request, f"Error updating testimonial: {str(e)}")
            return redirect('testimonial_list')

@console_login_required
def delete_testimonial(request, id):
    testimonial_id = id

    try:
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)

        if request.method == "POST":
            name = testimonial.name
            testimonial.delete()
            messages.success(request, f"Testimonial by '{name}' deleted successfully!")
            return redirect('testimonial_list')

    except Exception as e:
        messages.error(request, f"Error deleting testimonial: {str(e)}")
        return redirect('testimonial_list')

@console_login_required
def toggle_testimonial_status(request, testimonial_id):
    try:
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)

        testimonial.is_active = not testimonial.is_active
        testimonial.save()

        status_text = "Active" if testimonial.is_active else "Deactive"
        badge_class = "bg-success" if testimonial.is_active else "bg-danger"

        url = reverse("toggle_testimonial_status", args=[testimonial.id])

        return HttpResponse(
            f'<span hx-get="{url}" '
            f'hx-target="this" hx-swap="outerHTML" '
            f'class="badge {badge_class}" style="cursor:pointer;">'
            f'{status_text}</span>'
        )

    except Testimonial.DoesNotExist:
        raise Http404("Testimonial not found")

    except Exception:
        return HttpResponse(
            '<span class="badge bg-warning text-dark">Error</span>'
        )


# ===================== RESULT STATISTIC =====================
@console_login_required
def result_statistic_list(request):
    if request.method == "POST":
        try:
            title = request.POST.get('title', '').strip()
            value = request.POST.get('value', '').strip()
            description = request.POST.get('description', '').strip()
            icon = request.POST.get('icon', '').strip()
            order = request.POST.get('order', '0').strip() or '0'
            is_active = request.POST.get('is_active') == 'on'

            errors = []
            if not title:
                errors.append("Title is required.")
            elif len(title) > 200:
                errors.append("Title must be 200 characters or fewer.")

            if not value:
                errors.append("Value is required.")
            elif len(value) > 100:
                errors.append("Value must be 100 characters or fewer.")

            if not icon:
                errors.append("Icon class is required (e.g. fas fa-chart-line).")

            if not order.lstrip('-').isdigit():
                errors.append("Order must be a whole number.")

            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('result_statistic_list')

            ResultStatistic.objects.create(
                title=title,
                value=value,
                description=description,
                icon=icon,
                order=int(order),
                status=True,
                is_active=is_active,
            )

            messages.success(request, f"Result statistic '{title}' created successfully!")
            return redirect('result_statistic_list')

        except Exception as e:
            messages.error(request, f"Error creating result statistic: {str(e)}")
            return redirect('result_statistic_list')

    return render(
        request,
        'General_settings/general_setting_page/Result_Statistic/result_statistic_list.html'
    )


@console_login_required
def get_details_result_statistic(request):
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('search')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')

            if get_edit:
                stat = get_object_or_404(ResultStatistic, id=get_edit)
                return render(
                    request,
                    'General_settings/general_setting_page/Result_Statistic/components/result_statistic_edit.html',
                    {'stat': stat}
                )

            if get_delete:
                stat = get_object_or_404(ResultStatistic, id=get_delete)
                return render(
                    request,
                    'General_settings/general_setting_page/Result_Statistic/components/result_statistic_delete.html',
                    {'stat': stat}
                )

            query = Q()
            if search:
                query = Q(title__icontains=search) | Q(value__icontains=search)

            stats = ResultStatistic.objects.filter(query).order_by('order')

            paginator = Paginator(stats, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            return render(
                request,
                'General_settings/general_setting_page/Result_Statistic/components/result_statistic_table.html',
                {'stats': page_obj}
            )

        except Exception as e:
            return HttpResponse(f"Error loading data: {str(e)}", status=500)


@console_login_required
def update_result_statistic(request, id):
    stat = get_object_or_404(ResultStatistic, id=id)

    if request.method == 'POST':
        try:
            title = request.POST.get('u_title', '').strip()
            value = request.POST.get('u_value', '').strip()
            description = request.POST.get('u_description', '').strip()
            icon = request.POST.get('u_icon', '').strip()
            order = request.POST.get('u_order', '0').strip() or '0'
            is_active = request.POST.get('u_is_active') == 'on'

            errors = []
            if not title:
                errors.append("Title is required.")
            elif len(title) > 200:
                errors.append("Title must be 200 characters or fewer.")

            if not value:
                errors.append("Value is required.")
            elif len(value) > 100:
                errors.append("Value must be 100 characters or fewer.")

            if not icon:
                errors.append("Icon class is required (e.g. fas fa-chart-line).")

            if not order.lstrip('-').isdigit():
                errors.append("Order must be a whole number.")

            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('result_statistic_list')

            stat.title = title
            stat.value = value
            stat.description = description
            stat.icon = icon
            stat.order = int(order)
            stat.is_active = is_active
            stat.save()

            messages.success(request, f"Result statistic '{title}' updated successfully!")
            return redirect('result_statistic_list')

        except Exception as e:
            messages.error(request, f"Error updating result statistic: {str(e)}")
            return redirect('result_statistic_list')


@console_login_required
def delete_result_statistic(request, id):
    stat = get_object_or_404(ResultStatistic, id=id)

    try:
        if request.method == "POST":
            title = stat.title
            stat.delete()
            messages.success(request, f"Result statistic '{title}' deleted successfully!")
            return redirect('result_statistic_list')

    except Exception as e:
        messages.error(request, f"Error deleting result statistic: {str(e)}")
        return redirect('result_statistic_list')


@console_login_required
def toggle_result_statistic_status(request, stat_id):
    try:
        stat = get_object_or_404(ResultStatistic, id=stat_id)

        stat.is_active = not stat.is_active
        stat.save()

        status_text = "Active" if stat.is_active else "Deactive"
        badge_class = "bg-success" if stat.is_active else "bg-danger"

        url = reverse("toggle_result_statistic_status", args=[stat.id])

        return HttpResponse(
            f'<span hx-get="{url}" '
            f'hx-target="this" hx-swap="outerHTML" '
            f'class="badge {badge_class}" style="cursor:pointer;">'
            f'{status_text}</span>'
        )

    except ResultStatistic.DoesNotExist:
        raise Http404("Result statistic not found")

    except Exception:
        return HttpResponse(
            '<span class="badge bg-warning text-dark">Error</span>'
        )


@console_login_required
def project_category_list(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            icon = request.POST.get('icon', '').strip()
            color = request.POST.get('color', '#1976d2').strip()
            order = request.POST.get('order', 0)

            if not name:
                messages.error(request, "Project category name is required.")
                return redirect('project_category_list')

            # Check for duplicates (case-insensitive)
            if ProjectCategory.objects.filter(name__iexact=name).exists():
                messages.error(request, f"A project category with the name '{name}' already exists.")
                return redirect('project_category_list')

            # Get the logged-in admin from session
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, "User not authenticated. Please login again.")
                return redirect('state_list')

            try:
                console_admin = ConsoleAdminDetails.objects.get(id=user_id)
            except ConsoleAdminDetails.DoesNotExist:
                messages.error(request, "Admin user not found.")
                return redirect('state_list')

            # Generate slug automatically
            slug = slugify(name)

            # Create the ProjectCategory
            project_category = ProjectCategory.objects.create(
                console_full_name=console_admin,
                name=name,
                slug=slug,
                description=description,
                icon=icon,
                color=color,
                order=order
            )

            messages.success(request, f"Project category '{name}' created successfully!")
            return redirect('project_category_list')

        except Exception as e:
            messages.error(request, f"Error creating project category: {str(e)}")
            return redirect('project_category_list')

    # For GET request, display all categories
    categories = ProjectCategory.objects.all()
    return render(request, 'General_settings/general_setting_page/Project_Cat/project_category_list.html', {
        'categories': categories
    })


@console_login_required
def get_project_category_details(request):
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('search')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')

            if get_edit:
                category = get_object_or_404(ProjectCategory, id=get_edit)
                context = {'category': category}
                return render(request, 'General_settings/general_setting_page/Project_Cat/project_cat_edit.html', context)

            if get_delete:
                category = get_object_or_404(ProjectCategory, id=get_delete)
                context = {'category': category}
                return render(request, 'General_settings/general_setting_page/Project_Cat/project_cat_delete.html', context)

            query = Q()
            if search:
                query = Q(name__icontains=search)

            categories = ProjectCategory.objects.filter(query).order_by('-created_at')
            paginator = Paginator(categories, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            context = {'categories': page_obj}
            return render(request, 'General_settings/general_setting_page/Project_Cat/project_cat_table.html', context)

        except Exception as e:
            return HttpResponse(f"Error loading data: {str(e)}", status=500)


@console_login_required
def update_project_category(request, id):
    category_id = id
    if request.method == 'POST':
        try:
            category = get_object_or_404(ProjectCategory, id=category_id)

            name = request.POST.get('u_name', '').strip()
            description = request.POST.get('u_description', '').strip()
            icon = request.POST.get('u_icon', '').strip()
            color = request.POST.get('u_color', '#1976d2').strip()
            order = request.POST.get('u_order', 0)

            if not name:
                messages.error(request, "Project category name is required.")
                return redirect('project_category_list')

            # Check duplicates excluding current record
            if ProjectCategory.objects.filter(name__iexact=name).exclude(id=category_id).exists():
                messages.error(request, f"A project category with the name '{name}' already exists.")
                return redirect('project_category_list')

            # Update admin reference if session available
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    console_admin = ConsoleAdminDetails.objects.get(id=user_id)
                    category.console_full_name = console_admin
                except ConsoleAdminDetails.DoesNotExist:
                    pass

            # Update fields
            category.name = name
            category.slug = slugify(name)
            category.description = description
            category.icon = icon
            category.color = color
            category.order = order
            category.save()

            messages.success(request, f"Project category '{name}' updated successfully!")
            return redirect('project_category_list')

        except Exception as e:
            messages.error(request, f"Error updating project category: {str(e)}")
            return redirect('project_category_list')


@console_login_required
def delete_project_category(request, id):
    category_id = id
    try:
        category = get_object_or_404(ProjectCategory, id=category_id)
        if request.method == "POST":
            name = category.name
            category.delete()
            messages.success(request, f"Project category '{name}' deleted successfully!")
            return redirect('project_category_list')

    except Exception as e:
        messages.error(request, f"Error deleting project category: {str(e)}")
        return redirect('project_category_list')


@console_login_required
def toggle_project_category_status(request, category_id):
    try:
        category = get_object_or_404(ProjectCategory, id=category_id)

        # Toggle is_active
        category.is_active = not category.is_active
        category.save()

        status_text = "Active" if category.is_active else "Deactive"
        badge_class = "bg-success" if category.is_active else "bg-danger"
        url = reverse("toggle_project_category_status", args=[category.id])

        return HttpResponse(
            f'<span hx-get="{url}" '
            f'hx-target="this" hx-swap="outerHTML" '
            f'class="badge {badge_class}" style="cursor:pointer;">'
            f'{status_text}</span>'
        )

    except ProjectCategory.DoesNotExist:
        raise Http404("Project category not found.")
    except Exception as e:
        messages.error(request, "Unexpected error", extra_tags="danger")
        return HttpResponse(
            '<span class="badge bg-warning text-dark" style="cursor: not-allowed;">Error</span>'
        )


@console_login_required
def portfolio_project_list(request):
    if request.method == "POST":
        try:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            category_id = request.POST.get('category')
            client = request.POST.get('client', '').strip()
            project_date = request.POST.get('project_date')
            technologies = request.POST.get('technologies', '').strip()
            is_featured = request.POST.get('is_featured') == 'on'
            order = request.POST.get('order', 0)

            # Validate required fields
            if not title or not description or not category_id or not project_date:
                messages.error(request, "Title, Description, Category, and Project Date are required.")
                return redirect('portfolio_project_list')

            # Validate category
            try:
                category = ProjectCategory.objects.get(id=category_id)
            except ProjectCategory.DoesNotExist:
                messages.error(request, "Selected category does not exist.")
                return redirect('portfolio_project_list')

            # Validate duplicate project title (optional)
            if PortfolioProject.objects.filter(title__iexact=title).exists():
                messages.error(request, f"A project with the title '{title}' already exists.")
                return redirect('portfolio_project_list')

            # Handle image upload
            image = request.FILES.get('image')
            if not image:
                messages.error(request, "Project image is required.")
                return redirect('portfolio_project_list')

            # Create the PortfolioProject
            project = PortfolioProject.objects.create(
                title=title,
                description=description,
                short_description=short_description,
                image=image,
                category=category,
                client=client,
                project_date=project_date,
                technologies=technologies,
                is_featured=is_featured,
                order=order
            )

            messages.success(request, f"Project '{title}' created successfully!")
            return redirect('portfolio_project_list')

        except Exception as e:
            messages.error(request, f"Error creating project: {str(e)}")
            return redirect('portfolio_project_list')

    # GET request - list all projects
    projects = PortfolioProject.objects.select_related('category').all().order_by('order', '-project_date')
    categories = ProjectCategory.objects.filter(is_active=True).order_by('order', 'name')

    return render(request, 'General_settings/general_setting_page/Portfolio/portfolio_project_list.html', {
        'projects': projects,
        'categories': categories
    })
    


@console_login_required
def get_portfolio_project_details(request):
    """
    Handles HTMX requests for search, edit, and delete modals for PortfolioProject.
    """
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('search')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')
            get_view = request.GET.get('get_view')
            
            if get_view:
                project = get_object_or_404(PortfolioProject, id=get_view)
                context = {'project': project}
                return render(request, 'General_settings/general_setting_page/Portfolio/Portfolio_com/portfolio_project_view.html', context)

            # Edit modal
            if get_edit:
                project = get_object_or_404(PortfolioProject, id=get_edit)
                context = {'project': project, 'categories': ProjectCategory.objects.filter(is_active=True)}
                return render(request, 'General_settings/general_setting_page/Portfolio/Portfolio_com/portfolio_project_edit.html', context)
            
            
            # Delete modal
            if get_delete:
                project = get_object_or_404(PortfolioProject, id=get_delete)
                context = {'project': project}
                return render(request, 'General_settings/general_setting_page/Portfolio/Portfolio_com/portfolio_project_delete.html', context)
            
            

            # Table search/filter
            query = Q()
            if search:
                query = Q(title__icontains=search) | Q(client__icontains=search) | Q(category__name__icontains=search)

            projects = PortfolioProject.objects.filter(query).select_related('category').order_by('order', '-project_date')
            paginator = Paginator(projects, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            context = {'projects': page_obj}
            return render(request, 'General_settings/general_setting_page/Portfolio/Portfolio_com/portfolio_project_table.html', context)
        

        except Exception as e:
            return HttpResponse(f"Error loading data: {str(e)}", status=500)


@console_login_required
def update_portfolio_project(request, id):
    """
    Updates a PortfolioProject record.
    """
    project = get_object_or_404(PortfolioProject, id=id)

    if request.method == "POST":
        try:
            title = request.POST.get('u_title', '').strip()
            description = request.POST.get('u_description', '').strip()
            short_description = request.POST.get('u_short_description', '').strip()
            category_id = request.POST.get('u_category')
            client = request.POST.get('u_client', '').strip()
            project_date = request.POST.get('u_project_date')
            technologies = request.POST.get('u_technologies', '').strip()
            is_featured = request.POST.get('u_is_featured') == 'on'
            is_active = request.POST.get('u_is_active') == 'on'
            order = request.POST.get('u_order', 0)

            # Validation
            if not title or not description or not category_id or not project_date:
                messages.error(request, "Title, Description, Category, and Project Date are required.")
                return redirect('portfolio_project_list')

            # Duplicate check
            if PortfolioProject.objects.filter(title__iexact=title).exclude(id=project.id).exists():
                messages.error(request, f"A project with the title '{title}' already exists.")
                return redirect('portfolio_project_list')

            # Get category
            try:
                category = ProjectCategory.objects.get(id=category_id)
            except ProjectCategory.DoesNotExist:
                messages.error(request, "Selected category does not exist.")
                return redirect('portfolio_project_list')

            # Update fields
            project.title = title
            project.description = description
            project.short_description = short_description
            project.category = category
            project.client = client
            project.project_date = project_date
            project.technologies = technologies
            project.is_featured = is_featured
            project.is_active = is_active
            project.order = order

            # Update admin reference (optional)
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    console_admin = ConsoleAdminDetails.objects.get(id=user_id)
                    # You may link this to the project if desired
                except ConsoleAdminDetails.DoesNotExist:
                    pass

            # Update image if uploaded
            if request.FILES.get('u_image'):
                project.image = request.FILES.get('u_image')

            project.save()

            messages.success(request, f"Project '{title}' updated successfully!")
            return redirect('portfolio_project_list')

        except Exception as e:
            messages.error(request, f"Error updating project: {str(e)}")
            return redirect('portfolio_project_list')


@console_login_required
def delete_portfolio_project(request, id):
    """
    Deletes a PortfolioProject record.
    """
    project = get_object_or_404(PortfolioProject, id=id)

    if request.method == "POST":
        try:
            title = project.title
            project.delete()
            messages.success(request, f"Project '{title}' deleted successfully!")
            return redirect('portfolio_project_list')
        except Exception as e:
            messages.error(request, f"Error deleting project: {str(e)}")
            return redirect('portfolio_project_list')


@console_login_required
def toggle_portfolio_project_status(request, project_id):
    """
    Toggles the is_active status of a PortfolioProject.
    """
    try:
        project = get_object_or_404(PortfolioProject, id=project_id)

        # Toggle active status
        project.is_active = not project.is_active
        project.save()

        status_text = "Active" if project.is_active else "Inactive"
        badge_class = "bg-success" if project.is_active else "bg-danger"

        url = reverse("toggle_portfolio_project_status", args=[project.id])

        return HttpResponse(
            f'<span hx-get="{url}" '
            f'hx-target="this" hx-swap="outerHTML" '
            f'class="badge {badge_class}" style="cursor:pointer;">'
            f'{status_text}</span>'
        )

    except PortfolioProject.DoesNotExist:
        raise Http404("Project not found.")

    except Exception as e:
        return HttpResponse(
            '<span class="badge bg-warning text-dark" style="cursor: not-allowed;">Error</span>'
        )



@console_login_required
def contact_message_list(request):
    """List and create contact messages"""
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not name or not email or not subject or not message_text:
            messages.error(request, "All fields except phone are required.")
            return redirect('contact_message_list')

        user_id = request.session.get('user_id')
        console_admin = ConsoleAdminDetails.objects.filter(id=user_id).first() if user_id else None

        try:
            ContactMessage.objects.create(
                console_full_name=console_admin,
                name=name,
                email=email,
                subject=subject,
                message=message_text,
                phone=phone or None
            )
            messages.success(request, f"Message from '{name}' saved successfully!")
        except Exception as e:
            messages.error(request, f"Error saving message: {str(e)}")

        return redirect('contact_message_list')

    # List messages
    search = request.GET.get('search', '').strip()
    query = Q()
    if search:
        query = Q(name__icontains=search) | Q(email__icontains=search) | Q(subject__icontains=search)

    messages_qs = ContactMessage.objects.filter(query).order_by('-created_date')
    paginator = Paginator(messages_qs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {'messages': page_obj}
    return render(request, 'General_settings/general_setting_page/ContactMessage/contact_message_list.html', context)


@console_login_required
def get_contact_message_details(request):
    """
    Handles HTMX requests for search, view, edit, and delete modals for ContactMessage.
    """
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('search')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')


            # ------------------------------
            # Edit Modal
            # ------------------------------
            if get_edit:
                contact_message = get_object_or_404(ContactMessage, id=get_edit)
                context = {'contact_message': contact_message}
                return render(
                    request,
                    'General_settings/general_setting_page/ContactMessage/contact_message_edit.html',
                    context
                )

            # ------------------------------
            # Delete Modal
            # ------------------------------
            if get_delete:
                contact_message = get_object_or_404(ContactMessage, id=get_delete)
                context = {'contact_message': contact_message}
                return render(
                    request,
                    'General_settings/general_setting_page/ContactMessage/contact_message_delete.html',
                    context
                )

            # ------------------------------
            # Table search/filter
            # ------------------------------
            query = Q()
            if search:
                query = (
                    Q(name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(subject__icontains=search) |
                    Q(message__icontains=search)
                )

            messages_qs = ContactMessage.objects.filter(query).order_by('-created_date')
            paginator = Paginator(messages_qs, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            context = {'messages': page_obj}
            return render(
                request,
                'General_settings/general_setting_page/ContactMessage/contact_message_table.html',
                context
            )

        except Exception as e:
            return HttpResponse(f"Error loading data: {str(e)}", status=500)


# -------------------------------
# Edit / Update Message
# -------------------------------
@console_login_required
def update_contact_message(request, id):
    message_id = id
    contact_message = get_object_or_404(ContactMessage, id=message_id)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not name or not email or not subject or not message_text:
            messages.error(request, "All fields except phone are required.")
            return redirect('contact_message_list')

        user_id = request.session.get('user_id')
        console_admin = ConsoleAdminDetails.objects.filter(id=user_id).first() if user_id else None

        contact_message.name = name
        contact_message.email = email
        contact_message.subject = subject
        contact_message.message = message_text
        contact_message.phone = phone or None
        if console_admin:
            contact_message.console_full_name = console_admin

        contact_message.save()
        messages.success(request, f"Message from '{name}' updated successfully!")
        return redirect('contact_message_list')

    context = {'contact_message': contact_message}
    return render(request, 'General_settings/general_setting_page/ContactMessage/contact_message_edit.html', context)


# -------------------------------
# Delete Message
# -------------------------------
@console_login_required
def delete_contact_message(request, id):
    message_id = id
    contact_message = get_object_or_404(ContactMessage, id=message_id)

    if request.method == "POST":
        contact_message.delete()
        messages.success(request, f"Message from '{contact_message.name}' deleted successfully!")
        return redirect('contact_message_list')

    context = {'contact_message': contact_message}
    return render(request, 'General_settings/general_setting_page/ContactMessage/contact_message_delete.html', context)


# -------------------------------
# Toggle Message Status
# -------------------------------
@console_login_required
def toggle_contact_message_status(request, message_id):
    contact_message = get_object_or_404(ContactMessage, id=message_id)
    contact_message.status = not contact_message.status
    contact_message.save()

    status_text = "Active" if contact_message.status else "Inactive"
    badge_class = "bg-success" if contact_message.status else "bg-danger"
    url = reverse("toggle_contact_message_status", args=[contact_message.id])

    return HttpResponse(
        f'<span hx-get="{url}" hx-target="this" hx-swap="outerHTML" '
        f'class="badge {badge_class}" style="cursor:pointer;">{status_text}</span>'
    )

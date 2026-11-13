from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Lab, Resource, Complaint, Suggestion, Stock, Enquiry, SiteSettings, HeroSlide
from .forms import UserRegistrationForm, ComplaintForm, SuggestionForm, ResourceForm, LabAdminForm, StockForm, EnquiryForm, LabForm, UserEditForm, SiteSettingsForm, HeroSlideForm

# ------ Landing & Auth ------
def landing_page(request):
    if request.user.is_authenticated:
        if request.user.is_main_admin():
            return redirect('admin_dashboard')
        elif request.user.is_lab_admin():
            return redirect('lab_admin_dashboard')
        else:
            return redirect('dashboard')
            
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your enquiry has been submitted. We will get back to you soon.')
            return redirect('landing')
    else:
        form = EnquiryForm()
        
    stats = {
        'total_users': User.objects.filter(role='STUDENT').count(),
        'total_complaints': Complaint.objects.count(),
        'total_suggestions': Suggestion.objects.count(),
        'solved_complaints': Complaint.objects.filter(status='RESOLVED').count(),
    }
    slides = HeroSlide.objects.filter(is_active=True)
    return render(request, 'Reso_Track/landing.html', {'form': form, 'stats': stats, 'slides': slides})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'Reso_Track/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if user.status == 'Blocked':
                messages.error(request, 'Your account is blocked by the admin.')
                return render(request, 'Reso_Track/login.html')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            if user.is_main_admin():
                return redirect('admin_dashboard')
            elif user.is_lab_admin():
                return redirect('lab_admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'Reso_Track/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('landing')

@login_required
def profile_view(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('name', request.user.first_name)
        new_pwd = request.POST.get('password')
        if new_pwd:
            request.user.set_password(new_pwd)
        request.user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
        
    return render(request, 'Reso_Track/profile.html')

# ------ User Dashboard & Modules ------
@login_required
def user_dashboard(request):
    if not request.user.is_student():
        return redirect('landing')
    
    complaints = Complaint.objects.filter(user=request.user).order_by('-date')[:5]
    suggestions = Suggestion.objects.filter(user=request.user).order_by('-date_submitted')[:5]
    
    context = {
        'complaints': complaints,
        'suggestions': suggestions,
        'complaint_count': Complaint.objects.filter(user=request.user).count(),
        'suggestion_count': Suggestion.objects.filter(user=request.user).count(),
    }
    return render(request, 'Reso_Track/user_dashboard.html', context)

@login_required
def resource_analyzer(request):
    dept = request.GET.get('department')
    lab_id = request.GET.get('lab')
    search = request.GET.get('search', '')
    
    resources = Resource.objects.all()
    if dept:
        resources = resources.filter(lab__department=dept)
    if lab_id:
        resources = resources.filter(lab_id=lab_id)
    if search:
        resources = resources.filter(resource_name__icontains=search)
        
    labs = Lab.objects.all()
    context = {
        'resources': resources,
        'labs': labs,
        'departments': User.DEPT_CHOICES
    }
    return render(request, 'Reso_Track/resources.html', context)

@login_required
def add_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, 'Complaint submitted successfully.')
            return redirect('complaint_status')
    else:
        form = ComplaintForm()
    return render(request, 'Reso_Track/add_complaint.html', {'form': form})

@login_required
def complaint_status(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-date')
    return render(request, 'Reso_Track/complaint_status.html', {'complaints': complaints})

@login_required
def add_suggestion(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.user = request.user
            suggestion.save()
            messages.success(request, 'Suggestion submitted successfully.')
            return redirect('dashboard')
    else:
        form = SuggestionForm()
    return render(request, 'Reso_Track/add_suggestion.html', {'form': form})

@login_required
def delete_complaint(request, c_id):
    complaint = get_object_or_404(Complaint, id=c_id, user=request.user)
    complaint.delete()
    messages.success(request, 'Complaint deleted successfully.')
    return redirect('complaint_status')

@login_required
def delete_suggestion(request, s_id):
    suggestion = get_object_or_404(Suggestion, id=s_id, user=request.user)
    suggestion.delete()
    messages.success(request, 'Suggestion deleted successfully.')
    return redirect('dashboard')

# ------ Admin Dashboard & Modules ------
@login_required
def admin_dashboard(request):
    if not request.user.is_main_admin():
        return redirect('landing')
        
    context = {
        'total_users': User.objects.filter(role='STUDENT').count(),
        'total_complaints': Complaint.objects.count(),
        'resolved_complaints': Complaint.objects.filter(status='RESOLVED').count(),
        'pending_complaints': Complaint.objects.filter(status='PENDING').count(),
        'total_resources': Resource.objects.count(),
    }
    return render(request, 'Reso_Track/admin_dashboard.html', context)

@login_required
def admin_users(request):
    if not request.user.is_main_admin(): return redirect('landing')
    users = User.objects.filter(role='STUDENT')
    
    search = request.GET.get('search')
    dept = request.GET.get('department')
    
    if search:
        users = users.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
    
    if dept:
        users = users.filter(department=dept)
        
    return render(request, 'Reso_Track/admin_users.html', {
        'users': users,
        'departments': User.DEPT_CHOICES
    })

@login_required
def admin_remove_user(request, user_id):
    if not request.user.is_main_admin(): return redirect('landing')
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('admin_users')

@login_required
def admin_block_user(request, user_id):
    if not request.user.is_main_admin(): return redirect('landing')
    user = get_object_or_404(User, id=user_id)
    user.status = 'Blocked' if user.status == 'Active' else 'Active'
    user.save()
    messages.success(request, f"User status updated to {user.status}")
    return redirect('admin_users')

@login_required
def admin_labs(request):
    if not request.user.is_main_admin(): return redirect('landing')
    labs = Lab.objects.all()
    lab_admins = User.objects.filter(role='LAB_ADMIN')
    
    if request.method == 'POST':
        if 'add_lab' in request.POST:
            Lab.objects.create(
                department=request.POST.get('department'),
                lab_name=request.POST.get('lab_name'),
                lab_code=request.POST.get('lab_code'),
            )
            messages.success(request, "Lab created!")
            return redirect('admin_labs')
        elif 'add_admin' in request.POST:
            form = LabAdminForm(request.POST)
            if form.is_valid():
                admin_user = form.save()
                lab_id = request.POST.get('lab_id')
                if lab_id:
                    lab = Lab.objects.get(id=lab_id)
                    lab.lab_admin = admin_user
                    lab.save()
                messages.success(request, "Lab Admin created!")
                return redirect('admin_labs')
    
    form = LabAdminForm()
    return render(request, 'Reso_Track/admin_labs.html', {'labs': labs, 'lab_admins': lab_admins, 'form': form, 'departments': User.DEPT_CHOICES})

@login_required
def admin_complaints(request):
    if not request.user.is_main_admin(): return redirect('landing')
    Complaint.objects.filter(is_seen=False).update(is_seen=True)
    
    status = request.GET.get('status')
    complaints = Complaint.objects.all().order_by('-date')
    
    if status:
        complaints = complaints.filter(status=status)
        
    return render(request, 'Reso_Track/admin_complaints.html', {
        'complaints': complaints,
        'status_choices': Complaint.STATUS_CHOICES
    })

@login_required
def admin_approve_complaint(request, c_id):
    if not request.user.is_main_admin(): return redirect('landing')
    comp = get_object_or_404(Complaint, id=c_id)
    comp.status = 'APPROVED'
    comp.save()
    messages.success(request, 'Complaint approved and forwarded to Lab Admin.')
    return redirect('admin_complaints')

@login_required
def admin_reject_complaint(request, c_id):
    if not request.user.is_main_admin(): return redirect('landing')
    comp = get_object_or_404(Complaint, id=c_id)
    comp.status = 'REJECTED'
    comp.save()
    messages.success(request, 'Complaint rejected.')
    return redirect('admin_complaints')

@login_required
def admin_suggestions(request):
    if not request.user.is_main_admin(): return redirect('landing')
    Suggestion.objects.filter(is_seen_admin=False).update(is_seen_admin=True)
    
    status = request.GET.get('status')
    suggestions = Suggestion.objects.all().order_by('-date_submitted')
    
    if status:
        suggestions = suggestions.filter(status=status)
        
    if request.method == 'POST':
        s_id = request.POST.get('s_id')
        status_val = request.POST.get('status')
        sugg = get_object_or_404(Suggestion, id=s_id)
        sugg.status = status_val
        sugg.save()
        messages.success(request, 'Suggestion status updated.')
        return redirect('admin_suggestions')
        
    return render(request, 'Reso_Track/admin_suggestions.html', {
        'suggestions': suggestions,
        'status_choices': Suggestion.STATUS_CHOICES
    })
@login_required
def admin_delete_complaint(request, c_id):
    if not request.user.is_main_admin(): return redirect('landing')
    comp = get_object_or_404(Complaint, id=c_id)
    comp.delete()
    messages.success(request, 'Complaint deleted.')
    return redirect('admin_complaints')

@login_required
def admin_delete_suggestion(request, s_id):
    if not request.user.is_main_admin(): return redirect('landing')
    sugg = get_object_or_404(Suggestion, id=s_id)
    sugg.delete()
    messages.success(request, 'Suggestion deleted.')
    return redirect('admin_suggestions')

def admin_reports(request):
    if not request.user.is_main_admin(): return redirect('landing')
    
    dept_complaints = Complaint.objects.values('lab__department').annotate(count=Count('id'))
    status_counts = Resource.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'dept_complaints': dept_complaints,
        'status_counts': status_counts
    }
    return render(request, 'Reso_Track/admin_reports.html', context)

@login_required
def admin_enquiries(request):
    if not request.user.is_main_admin(): return redirect('landing')
    Enquiry.objects.filter(is_seen=False).update(is_seen=True)
    
    status = request.GET.get('status')
    enquiries = Enquiry.objects.all().order_by('-date_submitted')
    
    if status == 'responded':
        enquiries = enquiries.filter(is_responded=True)
    elif status == 'pending':
        enquiries = enquiries.filter(is_responded=False)
        
    return render(request, 'Reso_Track/admin_enquiries.html', {'enquiries': enquiries})

@login_required
def admin_edit_lab(request, l_id):
    if not request.user.is_main_admin(): return redirect('landing')
    lab = get_object_or_404(Lab, id=l_id)
    if request.method == 'POST':
        form = LabForm(request.POST, instance=lab)
        if form.is_valid():
            form.save()
            messages.success(request, "Lab updated!")
            return redirect('admin_labs')
    else:
        form = LabForm(instance=lab)
    return render(request, 'Reso_Track/admin_edit_lab.html', {'form': form, 'lab': lab})

@login_required
def admin_delete_lab(request, l_id):
    if not request.user.is_main_admin(): return redirect('landing')
    lab = get_object_or_404(Lab, id=l_id)
    lab.delete()
    messages.success(request, "Lab deleted!")
    return redirect('admin_labs')

@login_required
def admin_edit_lab_admin(request, user_id):
    if not request.user.is_main_admin(): return redirect('landing')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Lab Admin updated!")
            return redirect('admin_labs')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'Reso_Track/admin_edit_lab_admin.html', {'form': form, 'admin_user': user})

@login_required
def admin_delete_lab_admin(request, user_id):
    if not request.user.is_main_admin(): return redirect('landing')
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "Lab Admin deleted!")
    return redirect('admin_labs')

@login_required
def admin_reply_enquiry(request, e_id):
    if not request.user.is_main_admin(): return redirect('landing')
    enquiry = get_object_or_404(Enquiry, id=e_id)
    # Mark as seen when viewed
    if not enquiry.is_seen:
        enquiry.is_seen = True
        enquiry.save()
    return render(request, 'Reso_Track/admin_reply_enquiry.html', {'enquiry': enquiry})

@login_required
def admin_settings(request):
    if not request.user.is_main_admin(): return redirect('landing')
    
    settings = SiteSettings.objects.first()
    if not settings:
        settings = SiteSettings.objects.create()
        
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Website settings updated successfully.')
            return redirect('admin_settings')
    else:
        form = SiteSettingsForm(instance=settings)
        
    return render(request, 'Reso_Track/admin_settings.html', {'form': form})

@login_required
def admin_sliders(request):
    if not request.user.is_main_admin(): return redirect('landing')
    sliders = HeroSlide.objects.all()
    return render(request, 'Reso_Track/admin_sliders.html', {'sliders': sliders})

@login_required
def admin_add_slider(request):
    if not request.user.is_main_admin(): return redirect('landing')
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slide added.')
            return redirect('admin_sliders')
    else:
        form = HeroSlideForm()
    return render(request, 'Reso_Track/admin_slider_form.html', {'form': form, 'title': 'Add Slide'})

@login_required
def admin_edit_slider(request, s_id):
    if not request.user.is_main_admin(): return redirect('landing')
    slide = get_object_or_404(HeroSlide, id=s_id)
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slide updated.')
            return redirect('admin_sliders')
    else:
        form = HeroSlideForm(instance=slide)
    return render(request, 'Reso_Track/admin_slider_form.html', {'form': form, 'title': 'Edit Slide'})

@login_required
def admin_delete_slider(request, s_id):
    if not request.user.is_main_admin(): return redirect('landing')
    slide = get_object_or_404(HeroSlide, id=s_id)
    slide.delete()
    messages.success(request, 'Slide deleted.')
    return redirect('admin_sliders')

# ------ Lab Admin Dashboard & Modules ------
@login_required
def lab_admin_dashboard(request):
    if not request.user.is_lab_admin(): return redirect('landing')
    labs_managed = request.user.managed_labs.all()
    
    complaints = Complaint.objects.filter(lab__in=labs_managed, status__in=['APPROVED', 'IN_PROGRESS', 'RESOLVED']).order_by('-date')
    resources = Resource.objects.filter(lab__in=labs_managed)
    stocks = Stock.objects.filter(lab__in=labs_managed)
    suggestions = Suggestion.objects.filter(status='FORWARDED').order_by('-date_submitted')[:5]
    
    context = {
        'labs': labs_managed,
        'complaints': complaints,
        'resources': resources,
        'resource_count': resources.count(),
        'complaint_count': complaints.filter(status__in=['APPROVED', 'IN_PROGRESS']).count(),
        'stock_count': stocks.count(),
        'suggestions': suggestions
    }
    return render(request, 'Reso_Track/lab_admin_dashboard.html', context)

@login_required
def lab_add_resource(request):
    if not request.user.is_lab_admin(): return redirect('landing')
    labs_managed = request.user.managed_labs.all()
    
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        lab_id = request.POST.get('lab')
        lab = get_object_or_404(Lab, id=lab_id)
        if form.is_valid() and lab in labs_managed:
            resource = form.save(commit=False)
            resource.lab = lab
            resource.save()
            messages.success(request, 'Resource added successfully.')
            return redirect('lab_admin_dashboard')
    else:
        form = ResourceForm()
    return render(request, 'Reso_Track/lab_add_resource.html', {'form': form, 'labs': labs_managed})

@login_required
def lab_edit_resource(request, r_id):
    if not request.user.is_lab_admin(): return redirect('landing')
    resource = get_object_or_404(Resource, id=r_id, lab__lab_admin=request.user)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully.')
            return redirect('lab_admin_dashboard')
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'Reso_Track/lab_edit_resource.html', {'form': form, 'resource': resource})

@login_required
def lab_delete_resource(request, r_id):
    if not request.user.is_lab_admin(): return redirect('landing')
    resource = get_object_or_404(Resource, id=r_id, lab__lab_admin=request.user)
    resource.delete()
    messages.success(request, 'Resource deleted.')
    return redirect('lab_admin_dashboard')

@login_required
def lab_complaints(request):
    if not request.user.is_lab_admin(): return redirect('landing')
    labs = request.user.managed_labs.all()
    Complaint.objects.filter(lab__in=labs, is_seen=False).update(is_seen=True)
    complaints = Complaint.objects.filter(lab__in=labs, status__in=['APPROVED', 'IN_PROGRESS', 'RESOLVED']).order_by('-date')
    return render(request, 'Reso_Track/lab_complaints.html', {'complaints': complaints})

@login_required
def lab_update_complaint(request, c_id, status):
    if not request.user.is_lab_admin(): return redirect('landing')
    comp = get_object_or_404(Complaint, id=c_id, lab__lab_admin=request.user)
    if status in ['IN_PROGRESS', 'RESOLVED']:
        comp.status = status
        comp.save()
        messages.success(request, f'Complaint status updated to {status.replace("_", " ")}.')
    return redirect('lab_complaints')

@login_required
def lab_suggestions(request):
    if not request.user.is_lab_admin(): return redirect('landing')
    Suggestion.objects.filter(status='FORWARDED', is_seen_lab=False).update(is_seen_lab=True)
    suggestions = Suggestion.objects.filter(status='FORWARDED').order_by('-date_submitted')
    return render(request, 'Reso_Track/lab_suggestions.html', {'suggestions': suggestions})

@login_required
def lab_stocks(request):
    if not request.user.is_lab_admin(): return redirect('landing')
    labs = request.user.managed_labs.all()
    stocks = Stock.objects.filter(lab__in=labs)
    
    # Filtering
    filter_type = request.GET.get('filter_type')
    filter_val = request.GET.get('filter_val')
    
    if filter_type == 'year' and filter_val:
        stocks = stocks.filter(date__year=filter_val)
    elif filter_type == 'month' and filter_val:
        stocks = stocks.filter(date__month=filter_val)
    elif filter_type == 'day' and filter_val:
        stocks = stocks.filter(date__day=filter_val)
    elif filter_type == 'date' and filter_val:
        stocks = stocks.filter(date=filter_val)
        
    stocks = stocks.order_by('-date')
    return render(request, 'Reso_Track/lab_stocks.html', {'stocks': stocks})

@login_required
def lab_stocks_print(request):
    if not request.user.is_lab_admin(): return redirect('landing')
    labs = request.user.managed_labs.all()
    stocks = Stock.objects.filter(lab__in=labs)
    
    # Same filtering for print
    filter_type = request.GET.get('filter_type')
    filter_val = request.GET.get('filter_val')
    
    if filter_type == 'year' and filter_val:
        stocks = stocks.filter(date__year=filter_val)
    elif filter_type == 'month' and filter_val:
        stocks = stocks.filter(date__month=filter_val)
    elif filter_type == 'day' and filter_val:
        stocks = stocks.filter(date__day=filter_val)
    elif filter_type == 'date' and filter_val:
        stocks = stocks.filter(date=filter_val)
        
    stocks = stocks.order_by('-date')
    return render(request, 'Reso_Track/lab_stocks_print.html', {'stocks': stocks})

@login_required
def lab_add_stock(request):
    if not request.user.is_lab_admin(): return redirect('landing')
    labs = request.user.managed_labs.all()
    
    if request.method == 'POST':
        form = StockForm(request.POST)
        lab_id = request.POST.get('lab')
        lab = get_object_or_404(Lab, id=lab_id)
        if form.is_valid() and lab in labs:
            stock = form.save(commit=False)
            stock.lab = lab
            stock.save()
            messages.success(request, 'Stock details added successfully.')
            return redirect('lab_stocks')
    else:
        form = StockForm()
    return render(request, 'Reso_Track/lab_add_stock.html', {'form': form, 'labs': labs})

@login_required
def lab_delete_stock(request, s_id):
    if not request.user.is_lab_admin(): return redirect('landing')
    stock = get_object_or_404(Stock, id=s_id, lab__lab_admin=request.user)
    stock.delete()
    messages.success(request, 'Stock record deleted.')
    return redirect('lab_stocks')

@login_required
def lab_edit_stock(request, s_id):
    if not request.user.is_lab_admin(): return redirect('landing')
    stock = get_object_or_404(Stock, id=s_id, lab__lab_admin=request.user)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock details updated successfully.')
            return redirect('lab_stocks')
    else:
        form = StockForm(instance=stock)
    return render(request, 'Reso_Track/lab_edit_stock.html', {'form': form, 'stock': stock})

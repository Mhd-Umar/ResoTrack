from .models import Enquiry, Complaint, Suggestion, SiteSettings

def site_settings(request):
    settings = SiteSettings.objects.first()
    if not settings:
        # Create default settings if they don't exist
        settings = SiteSettings.objects.create()
    return {'site_settings': settings}

def notification_counts(request):
    if not request.user.is_authenticated:
        return {}
    
    counts = {}
    if request.user.is_main_admin():
        counts['admin_enquiries'] = Enquiry.objects.filter(is_seen=False).count()
        counts['admin_complaints'] = Complaint.objects.filter(is_seen=False).count()
        counts['admin_suggestions'] = Suggestion.objects.filter(is_seen_admin=False).count()
    
    if request.user.is_lab_admin():
        managed_labs = request.user.managed_labs.all()
        counts['lab_complaints'] = Complaint.objects.filter(lab__in=managed_labs, status='APPROVED', is_seen=False).count()
        counts['lab_suggestions'] = Suggestion.objects.filter(status='FORWARDED', is_seen_lab=False).count()
        
    return {'notif_counts': counts}

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('ADMIN', 'Main Admin'),
        ('LAB_ADMIN', 'Lab Administrator'),
    )
    
    DEPT_CHOICES = (
        ('CHE', 'Computer Hardware Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('AU', 'Automobile Engineering'),
        ('EE', 'Electrical Engineering'),
        ('WS', 'Workshop'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    department = models.CharField(max_length=5, choices=DEPT_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=20, default='Active') # Active, Blocked

    def is_student(self):
        return self.role == 'STUDENT'
        
    def is_main_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
        
    def is_lab_admin(self):
        return self.role == 'LAB_ADMIN'

class Lab(models.Model):
    department = models.CharField(max_length=5, choices=User.DEPT_CHOICES)
    lab_name = models.CharField(max_length=100)
    lab_code = models.CharField(max_length=20, unique=True)
    lab_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_labs', limit_choices_to={'role': 'LAB_ADMIN'})

    def __str__(self):
        return f"{self.lab_name} ({self.department})"


class Resource(models.Model):
    STATUS_CHOICES = (
        ('WORKING', 'Working'),
        ('MAINTENANCE', 'Maintenance'),
        ('NOT_WORKING', 'Not Working'),
    )

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='resources')
    resource_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WORKING')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.resource_name

class Complaint(models.Model):
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='complaints')
    complaint_text = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date = models.DateTimeField(auto_now_add=True)

    is_seen = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        user_display = "Anonymous" if self.is_anonymous else self.user.username
        return f"Complaint by {user_display} - {self.lab.lab_name}"


class Suggestion(models.Model):
    CATEGORY_CHOICES = (
        ('INFRASTRUCTURE', 'Infrastructure'),
        ('EQUIPMENT', 'Equipment'),
        ('MAINTENANCE', 'Maintenance'),
        ('SOFTWARE', 'Software'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('REVIEWED', 'Reviewed'),
        ('FORWARDED', 'Forwarded to Lab Admin'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suggestions')
    suggestion_text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_seen_admin = models.BooleanField(default=False)
    is_seen_lab = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        user_display = "Anonymous" if self.is_anonymous else self.user.username
        return f"Suggestion by {user_display} - {self.category}"

class Stock(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='stocks')
    stock_name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    bill_no = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.stock_name

class Enquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_responded = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    admin_response = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Enquiry from {self.name} - {self.subject}"

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Reso Track')
    logo = models.FileField(upload_to='site/', null=True, blank=True)
    hero_title = models.CharField(max_length=200, default='Smart Lab Resource Monitoring')
    hero_subtitle = models.TextField(default='Efficiently manage laboratory resources, complaints, and suggestions in one place.')
    contact_email = models.EmailField(default='admin@resotrack.com')
    contact_phone = models.CharField(max_length=20, default='+91 1234567890')
    about_text = models.TextField(default='Reso Track is a comprehensive solution for technical institutions to monitor and manage lab resources effectively.')
    
    # Hero Image options
    hero_image = models.FileField(upload_to='site/', null=True, blank=True)

    def __str__(self):
        return "Website Settings"

    class Meta:
        verbose_name_plural = "Site Settings"
class HeroSlide(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to='carousel/')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

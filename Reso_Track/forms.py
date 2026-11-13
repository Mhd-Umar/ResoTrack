from django import forms
from .models import User, Complaint, Suggestion, Resource, Lab, Stock, Enquiry, SiteSettings, HeroSlide

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'hero_subtitle': forms.Textarea(attrs={'rows': 3}),
            'about_text': forms.Textarea(attrs={'rows': 5}),
        }

class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = ['title', 'subtitle', 'image', 'order', 'is_active']
        widgets = {
            'subtitle': forms.Textarea(attrs={'rows': 2}),
        }

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'username', 'department', 'password']
        
    name = forms.CharField(max_length=150, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists!")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'STUDENT'
        user.first_name = self.cleaned_data["name"]
        if commit:
            user.save()
        return user


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['lab', 'complaint_text', 'priority', 'is_anonymous']

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['category', 'suggestion_text', 'is_anonymous']

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['resource_name', 'description', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False

class LabAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['name', 'username', 'password', 'department']
        
    name = forms.CharField(max_length=150, required=True)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'LAB_ADMIN'
        user.first_name = self.cleaned_data["name"]
        if commit:
            user.save()
        return user

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['stock_name', 'quantity', 'date', 'time', 'bill_no', 'price', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'})
        }

class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'subject', 'message']

class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ['department', 'lab_name', 'lab_code', 'lab_admin']

class UserEditForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'username', 'department', 'password']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user

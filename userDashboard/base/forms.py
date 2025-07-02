from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Complaints

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    is_employee = forms.BooleanField(required=False, initial=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_employee')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_employee = self.cleaned_data['is_employee']
        if commit:
            user.save()
        return user

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaints
        fields = ['title', 'complainant_name', 'complaint', 'assignee', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter complaint title'}),
            'complainant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter complaint details'}),
            'assignee': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show employees in assignee dropdown with full names
        employees = User.objects.filter(is_employee=True, is_active=True)
        self.fields['assignee'].queryset = employees
        self.fields['assignee'].empty_label = "Select an employee to assign"
        
        # Customize choices to show full name instead of username
        self.fields['assignee'].choices = [('', 'Select an employee to assign')] + [
            (user.id, user.full_name) for user in employees
        ]

class ComplaintStatusForm(forms.ModelForm):
    class Meta:
        model = Complaints
        fields = ['status', 'comments']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add comments (optional)'}),
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_employee', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_employee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email 
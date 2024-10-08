from .models import User
from django.contrib import admin
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import SetPasswordForm
from .models import User, UserType,SupervisorStakeholderAssignment
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.exceptions import ValidationError




class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': 'The two password fields didn’t match.',
    }

    # user_type = forms.ModelChoiceField(queryset=UserType.objects.all())
    user_type = forms.ModelChoiceField(
        queryset=UserType.objects.all(),
        required=False,
        label="User Type",
        help_text="Select the type of user."
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text='Enter a strong password.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        help_text='Enter the same password as above, for verification.'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'full_name',
                  'phone_number', 'password1', 'password2', 'user_type')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        help_text="Your new password must be at least 8 characters long."
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification."
    )

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        print(password1, password2)

        if password1 and password2 and password1 != password2:
            self.add_error('new_password2',
                           'The two password fields must match.')

        return cleaned_data


class StakeholderUserForm(forms.ModelForm):
    class Meta:

        model = User
        fields = ['email', 'full_name', 'phone_number', 'farm_image', 'length',
                  'breadth', 'expiry_date', 'pollution_certificate', 'coopcapacity', 'address']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        length = cleaned_data.get('length')
        
    
        print(length)
        breadth = cleaned_data.get('breadth')
        print(type(breadth))
        
        if length is not None and breadth is not None and (length <= 0 or breadth <= 0):
            raise forms.ValidationError("Length and breadth must be positive numbers.")
        
        
        
    def clean_farm_image(self):
        farm_image = self.cleaned_data.get('farm_image')

        # Check if an image was uploaded
        if farm_image:
            # Validate the file size (limit to 2 MB, for example)
            max_size = 2 * 1024 * 1024  # 2 MB
            if farm_image.size > max_size:
                raise forms.ValidationError("The image file is too large (max size is 2 MB).")

            # Validate the file type (only allow images)
            if not farm_image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError("Only image files (PNG, JPG, JPEG, GIF) are allowed.")
        else:
            raise forms.ValidationError("No image uploaded. Please upload a farm image.")

        return farm_image

    

    def clean_pollution_certificate(self):
        pdf = self.cleaned_data.get('pollution_certificate')

        # Check if the file is uploaded
        if not pdf:
            raise ValidationError("Please upload a PDF file.")

        # Check if the file has a valid extension
        if not pdf.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed to upload.")

        # Check if the file size is greater than 5 MB
        if pdf.size > 5 * 1024 * 1024:
            raise ValidationError("The PDF file is too large.")

        return pdf

  
    
    def clean_expiry_date(self):
        expiry_date=self.cleaned_data.get('expiry_date')
        print(expiry_date)
        if expiry_date and expiry_date < timezone.now().date():
            print("Expiry date")
            raise ValidationError("expiry date cannot be in the past")
        return expiry_date
    
    
class SupervisorStakeholderAssignmentForm(forms.ModelForm):
    class Meta:
        model = SupervisorStakeholderAssignment
        fields = ['supervisor', 'stakeholders']
    
    stakeholders = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(user_type__name='stakeholder'),  # Adjust filter if necessary
        widget=admin.widgets.FilteredSelectMultiple("Stakeholders", is_stacked=False),
        required=True
    )
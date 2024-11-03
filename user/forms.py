from .models import Supplier
from .models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import SetPasswordForm
from .models import User, UserType
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.exceptions import ValidationError
import re


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
                  'breadth', 'expiry_date', 'pollution_certificate', 'coopcapacity', 'address', 'plan_file']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    from .models import User


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
        fields = ['email', 'full_name', 'phone_number', 'name', 'farm_image', 'length',
                  'breadth', 'expiry_date', 'pollution_certificate', 'address', 'location', 'plan_file']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        length = cleaned_data.get('length')
        breadth = cleaned_data.get('breadth')

    # Check if length and breadth are positive numbers
        if length is not None and breadth is not None and (length <= 0 or breadth <= 0):
            raise forms.ValidationError(
                "Length and breadth must be positive numbers.")

        return cleaned_data

    def clean_farm_image(self):
        farm_image = self.cleaned_data.get('farm_image')

        # Check if an image was uploaded
        if farm_image:
            # Validate the file size (limit to 2 MB, for example)
            max_size = 2 * 1024 * 1024  # 2 MB
            if farm_image.size > max_size:
                raise forms.ValidationError(
                    "The image file is too large (max size is 2 MB).")

            # Validate the file type (only allow images)
            if not farm_image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(
                    "Only image files (PNG, JPG, JPEG, GIF) are allowed.")
        else:
            raise forms.ValidationError(
                "No image uploaded. Please upload a farm image.")

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
        expiry_date = self.cleaned_data.get('expiry_date')
        print(expiry_date)
        if expiry_date and expiry_date < timezone.now().date():
            print("Expiry date")
            raise ValidationError("expiry date cannot be in the past")
        return expiry_date

    def clean_farm_plan(self):
        pdf = self.cleaned_data.get('plan_file')

        # Check if the file is uploaded
        if not pdf:
            raise ValidationError("Please upload a PDF file.")

        # Validate file extension (case-insensitive)
        if not pdf.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed to upload.")

        # Validate file size (ensure it's under 5 MB)
        max_size_in_mb = 5  # 5 MB
        if pdf.size > max_size_in_mb * 1024 * 1024:  # Convert MB to bytes
            raise ValidationError(
                f"The PDF file is too large. The file size must not exceed {max_size_in_mb} MB.")

        return pdf


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_code', 'name', 'email', 'phone_number',
                  'address', 'is_active']  # Include is_active field

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Supplier.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already in use. Please choose a different one.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Supplier.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "This phone number is already in use. Please choose a different one.")
        return phone_number

    def clean_supplier_code(self):
        supplier_code = self.cleaned_data.get('supplier_code')
        if Supplier.objects.filter(supplier_code=supplier_code).exists():
            raise forms.ValidationError(
                "This supplier code is already in use. Please choose a different one.")
        return supplier_code

    def clean_farm_image(self):
        farm_image = self.cleaned_data.get('farm_image')

        # Check if an image was uploaded
        if farm_image:
            # Validate the file size (limit to 2 MB, for example)
            max_size = 2 * 1024 * 1024  # 2 MB
            if farm_image.size > max_size:
                raise forms.ValidationError(
                    "The image file is too large (max size is 2 MB).")

            # Validate the file type (only allow images)
            if not farm_image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(
                    "Only image files (PNG, JPG, JPEG, GIF) are allowed.")
        else:
            raise forms.ValidationError(
                "No image uploaded. Please upload a farm image.")

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
        expiry_date = self.cleaned_data.get('expiry_date')
        print(expiry_date)
        if expiry_date and expiry_date < timezone.now().date():
            print("Expiry date")
            raise ValidationError("expiry date cannot be in the past")
        return expiry_date

    def clean_address(self):
        address = self.cleaned_data.get('address')

        # Split the address by commas
        parts = [part.strip() for part in address.split(',')]

        # Validate that there are exactly 3 parts
        if len(parts) != 3:
            raise forms.ValidationError(
                "Address must be in the format 'farm name, location, pincode'.")

        farm_name, location, pincode = parts

        # Validate the pincode format (6-digit number)
        if not re.match(r'^\d{6}$', pincode):
            raise forms.ValidationError("Pincode must be a 6-digit number.")

        return address


def clean_plan_file(self):
    file = self.cleaned_data.get('plan_file')
    if file:
        # Validate file type
        if not (file.name.endswith('.pdf') or file.name.endswith('.jpg') or file.name.endswith('.jpeg') or file.name.endswith('.png')):
            raise ValidationError(
                "Only PDF, JPG, JPEG, and PNG files are allowed.")

        # Validate file size (e.g., max 5 MB)
        if file.size > 5 * 1024 * 1024:  # 5 MB limit
            raise ValidationError("File size must be under 5 MB.")

    return file


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_code', 'name', 'email', 'phone_number',
                  'address', 'is_active']  # Include is_active field

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Supplier.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already in use. Please choose a different one.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Supplier.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "This phone number is already in use. Please choose a different one.")
        return phone_number

    def clean_supplier_code(self):
        supplier_code = self.cleaned_data.get('supplier_code')
        if Supplier.objects.filter(supplier_code=supplier_code).exists():
            raise forms.ValidationError(
                "This supplier code is already in use. Please choose a different one.")
        return supplier_code

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
from .models import Vaccine


class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        "password_mismatch": "The two password fields didn’t match.",
    }

    # user_type = forms.ModelChoiceField(queryset=UserType.objects.all())
    user_type = forms.ModelChoiceField(
        queryset=UserType.objects.all(),
        required=False,
        label="User Type",
        help_text="Select the type of user.",
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="Enter a strong password.",
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "full_name",
            "phone_number",
            "password1",
            "password2",
            "user_type",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        help_text="Your new password must be at least 8 characters long.",
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification.",
    )

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        print(password1, password2)

        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "The two password fields must match.")

        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        "password_mismatch": "The two password fields didn’t match.",
    }

    # user_type = forms.ModelChoiceField(queryset=UserType.objects.all())
    user_type = forms.ModelChoiceField(
        queryset=UserType.objects.all(),
        required=False,
        label="User Type",
        help_text="Select the type of user.",
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="Enter a strong password.",
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "full_name",
            "phone_number",
            "password1",
            "password2",
            "user_type",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        help_text="Your new password must be at least 8 characters long.",
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification.",
    )

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        print(password1, password2)

        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "The two password fields must match.")

        return cleaned_data


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "supplier_code",
            "name",
            "email",
            "phone_number",
            "is_active",
        ]  # Include is_active field

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Supplier.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already in use. Please choose a different one."
            )
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if Supplier.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "This phone number is already in use. Please choose a different one."
            )
        return phone_number

    def clean_supplier_code(self):
        supplier_code = self.cleaned_data.get("supplier_code")
        if Supplier.objects.filter(supplier_code=supplier_code).exists():
            raise forms.ValidationError(
                "This supplier code is already in use. Please choose a different one."
            )
        return supplier_code

    def clean_farm_image(self):
        farm_image = self.cleaned_data.get("farm_image")

        # Check if an image was uploaded
        if farm_image:
            # Validate the file size (limit to 2 MB, for example)
            max_size = 2 * 1024 * 1024  # 2 MB
            if farm_image.size > max_size:
                raise forms.ValidationError(
                    "The image file is too large (max size is 2 MB)."
                )

            # Validate the file type (only allow images)
            if not farm_image.name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                raise forms.ValidationError(
                    "Only image files (PNG, JPG, JPEG, GIF) are allowed."
                )
        else:
            raise forms.ValidationError(
                "No image uploaded. Please upload a farm image."
            )

        return farm_image


    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get("expiry_date")
        print(expiry_date)
        if expiry_date and expiry_date < timezone.now().date():
            print("Expiry date")
            raise ValidationError("expiry date cannot be in the past")
        return expiry_date


class VaccineForm(forms.ModelForm):
    class Meta:
        model = Vaccine
        fields = ["name", "manufacturer", "doses_required", "interval_days"]


from .models import VaccinationRecord


class VaccinationRecordForm(forms.ModelForm):
    class Meta:
        model = VaccinationRecord
        fields = [
            "batch",
            "vaccine",
            "dose_number",
            "scheduled_date",
            "administered_date",
            "status",
        ]

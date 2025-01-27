from django import forms
from .models import HotelUser
from django.contrib.auth import get_user_model


User = get_user_model()


class HotelFormUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
            "full_name",
            "phone_number",
        ]


class HotelForm(forms.ModelForm):
    class Meta:
        model = HotelUser
        fields = ["hotel_name", "address", "hotel_license", "latitude", "longitude"]


class OrderForm(forms.Form):
    one_kg_count = forms.IntegerField(
        min_value=0, required=False, label="1 kg chickens", initial=0
    )
    two_kg_count = forms.IntegerField(
        min_value=0, required=False, label="2 kg chickens", initial=0
    )
    three_kg_count = forms.IntegerField(
        min_value=0, required=False, label="3 kg chickens", initial=0
    )

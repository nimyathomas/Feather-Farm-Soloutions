from django import forms
from user.models import User
from django.core.exceptions import ValidationError



class CustomerUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'phone_number', 'address','hotel_license']
 

    


class OrderForm(forms.Form):
    one_kg_count = forms.IntegerField(min_value=0, required=False, label="1 kg chickens", initial=0)
    two_kg_count = forms.IntegerField(min_value=0, required=False, label="2 kg chickens", initial=0)
    three_kg_count = forms.IntegerField(min_value=0, required=False, label="3 kg chickens", initial=0)

from django import forms
from .models import FeedRequest

class FeedRequestForm(forms.ModelForm):
    class Meta:
        model = FeedRequest
        fields = ['chick_batch', 'feed_amount']  # Assuming these are the fields the stakeholder fills

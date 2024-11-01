from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now  # Use timezone-aware date
from .models import DailyData
from .models import ChickBatch  # Make sure to import the ChickBatch model



class DailyDataForm(forms.ModelForm):
    class Meta:
        model = DailyData
        fields = [
            'date', 'alive_count', 'sick_chicks', 'weight_gain', 
            'feed_uplifted', 'water_consumption', 'temperature', 'mortality_count'
        ]

    def __init__(self, *args, **kwargs):
        super(DailyDataForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  # Add class to all fields
            
class BatchSelectionForm(forms.Form):
    batch = forms.ModelChoiceField(queryset=ChickBatch.objects.none(), label="Select Batch")

  

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Get user from kwargs
        super().__init__(*args, **kwargs)
        self.fields['batch'].queryset = ChickBatch.objects.filter(user=user)  # Filter 
        
class DailyComparisonForm(forms.Form):
    current_batch = forms.ModelChoiceField(queryset=ChickBatch.objects.none())  # Start with empty queryset
    past_batch = forms.ModelChoiceField(queryset=ChickBatch.objects.none())
    compare_day = forms.IntegerField(
        min_value=1, 
        max_value=40,
        error_messages={
            'min_value': 'The compare day must be at least 1.',
            'max_value': 'The compare day must be at most 40.',
        }
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        # Set the queryset for current_batch to include only batches for the user
        self.fields['current_batch'].queryset = ChickBatch.objects.filter(user=user)

        # Dynamically update past_batch queryset based on current_batch selection
        if self.is_bound and self.data.get('current_batch'):
            try:
                current_batch_id = int(self.data.get('current_batch'))
                self.fields['past_batch'].queryset = ChickBatch.objects.filter(user=user).exclude(id=current_batch_id)
            except (ValueError, TypeError):
                self.fields['past_batch'].queryset = ChickBatch.objects.filter(user=user)  # Fallback queryset
        else:
            self.fields['past_batch'].queryset = ChickBatch.objects.filter(user=user)  # Default queryset

    def clean_compare_day(self):
        compare_day = self.cleaned_data.get('compare_day')

        # Ensure that the compare_day is valid (between 1 and 40)
        if compare_day is None or compare_day < 1 or compare_day > 40:
            raise forms.ValidationError("The compare day must be between 1 and 40.")
        
        return compare_day
from .models import FeedMonitoring

class FeedMonitoringForm(forms.ModelForm):
    class Meta:
        model = FeedMonitoring
        fields = ['batch', 'date', 'feed_consumed', 'feed_wastage', 'feed_forecast']
        widgets = {
            
            'date': forms.DateInput(attrs={'type': 'date'}),  # Use a date picker for the date field
            'feed_consumed': forms.NumberInput(attrs={'step': '0.01'}),  # Allow decimal input
            'feed_forecast': forms.NumberInput(attrs={'step': '0.01'}),  # Allow decimal input
            'feed_wastage': forms.NumberInput(attrs={'step': '0.01'}),  # Allow decimal input
        }

    def clean_feed_consumed(self):
        feed_consumed = self.cleaned_data.get('feed_consumed')
        if feed_consumed < 0:
            raise forms.ValidationError("Feed consumed cannot be negative.")
        return feed_consumed

    def clean_feed_forecast(self):
        feed_forecast = self.cleaned_data.get('feed_forecast')
        if feed_forecast < 0:
            raise forms.ValidationError("Feed forecast cannot be negative.")
        return feed_forecast

    def clean_feed_wastage(self):
        feed_wastage = self.cleaned_data.get('feed_wastage')
        if feed_wastage < 0:
            raise forms.ValidationError("Feed wastage cannot be negative.")
        return feed_wastage

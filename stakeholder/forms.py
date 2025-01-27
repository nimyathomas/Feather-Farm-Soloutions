from django.contrib.auth import get_user_model
from .models import FeedMonitoring
from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now  # Use timezone-aware date
from .models import DailyData, ChickBatch, Farm


User = get_user_model()


class StakeholderUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
            "full_name",
            "phone_number",
        ]



from .models import Farm

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = [
            "name",
            "farm_image",
            "length",
            "breadth",
            "latitude",
            "longitude",
            "address",
            "established_date",
            "coopcapacity",
            "is_recommended",
            "plan_file",
            "expiry_date",
            "pollution_certificate",
            "certification_type",
            "certification_file",
        ]
        widgets = {
            "established_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }

class DailyDataForm(forms.ModelForm):
    class Meta:
        model = DailyData
        fields = [
            "date",
            "alive_count",
            "sick_chicks",
            "weight_gain",
            "feed_uplifted",
            "water_consumption",
            "temperature",
            "mortality_count",
        ]

    def __init__(self, *args, **kwargs):
        super(DailyDataForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # Add class to all fields
            field.widget.attrs.update({"class": "form-control"})


class ChickenBatchForm(forms.ModelForm):
    class Meta:
        model = ChickBatch
        fields = ["price_per_kg", "price_per_batch", "batch_status", "duration"]


class CompletedBatchUpdateForm(forms.ModelForm):
    """Form for updating count of chickens in 1kg, 2kg, and 3kg categories."""

    class Meta:
        model = ChickBatch
        fields = ["one_kg_count", "two_kg_count", "three_kg_count"]
        widgets = {
            "one_kg_count": forms.NumberInput(
                attrs={"min": 0, "class": "form-control", "id": "one-kg-count"}
            ),
            "two_kg_count": forms.NumberInput(
                attrs={"min": 0, "class": "form-control", "id": "two-kg-count"}
            ),
            "three_kg_count": forms.NumberInput(
                attrs={"min": 0, "class": "form-control", "id": "three-kg-count"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        one_kg_count = cleaned_data.get("one_kg_count", 0)
        two_kg_count = cleaned_data.get("two_kg_count", 0)
        three_kg_count = cleaned_data.get("three_kg_count", 0)

        # Total count from form input
        total_count = one_kg_count + two_kg_count + three_kg_count

        # Get the batch instance being updated to check live chick count
        batch = self.instance
        if total_count > batch.available_chickens:
            raise forms.ValidationError(
                f"The total count ({total_count}) exceeds the number of live chickens available ({batch.live_chick_count})."
            )

        return cleaned_data


class BatchSelectionForm(forms.Form):
    batch = forms.ModelChoiceField(
        queryset=ChickBatch.objects.none(), label="Select Batch"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")  # Get user from kwargs
        super().__init__(*args, **kwargs)
        self.fields["batch"].queryset = ChickBatch.objects.filter(user=user)  # Filter


class DailyComparisonForm(forms.Form):
    current_batch = forms.ModelChoiceField(
        queryset=ChickBatch.objects.none()
    )  # Start with empty queryset
    past_batch = forms.ModelChoiceField(queryset=ChickBatch.objects.none())
    compare_day = forms.IntegerField(
        min_value=1,
        max_value=40,
        error_messages={
            "min_value": "The compare day must be at least 1.",
            "max_value": "The compare day must be at most 40.",
        },
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        # Set the queryset for current_batch to include only batches for the user
        self.fields["current_batch"].queryset = ChickBatch.objects.filter(user=user)

        # Dynamically update past_batch queryset based on current_batch selection
        if self.is_bound and self.data.get("current_batch"):
            try:
                current_batch_id = int(self.data.get("current_batch"))
                self.fields["past_batch"].queryset = ChickBatch.objects.filter(
                    user=user
                ).exclude(id=current_batch_id)
            except (ValueError, TypeError):
                self.fields["past_batch"].queryset = ChickBatch.objects.filter(
                    user=user
                )  # Fallback queryset
        else:
            self.fields["past_batch"].queryset = ChickBatch.objects.filter(
                user=user
            )  # Default queryset

    def clean_compare_day(self):
        compare_day = self.cleaned_data.get("compare_day")

        # Ensure that the compare_day is valid (between 1 and 40)
        if compare_day is None or compare_day < 1 or compare_day > 40:
            raise forms.ValidationError("The compare day must be between 1 and 40.")

        return compare_day


class FeedMonitoringForm(forms.ModelForm):
    class Meta:
        model = FeedMonitoring
        fields = ["batch", "date", "feed_consumed", "feed_wastage", "feed_forecast"]
        widgets = {
            # Use a date picker for the date field
            "date": forms.DateInput(attrs={"type": "date"}),
            # Allow decimal input
            "feed_consumed": forms.NumberInput(attrs={"step": "0.01"}),
            # Allow decimal input
            "feed_forecast": forms.NumberInput(attrs={"step": "0.01"}),
            # Allow decimal input
            "feed_wastage": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def clean_feed_consumed(self):
        feed_consumed = self.cleaned_data.get("feed_consumed")
        if feed_consumed < 0:
            raise forms.ValidationError("Feed consumed cannot be negative.")
        return feed_consumed

    def clean_feed_forecast(self):
        feed_forecast = self.cleaned_data.get("feed_forecast")
        if feed_forecast < 0:
            raise forms.ValidationError("Feed forecast cannot be negative.")
        return feed_forecast

    def clean_feed_wastage(self):
        feed_wastage = self.cleaned_data.get("feed_wastage")
        if feed_wastage < 0:
            raise forms.ValidationError("Feed wastage cannot be negative.")
        return feed_wastage

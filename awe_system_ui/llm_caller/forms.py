import pandas as pd
from django import forms
from django.core.exceptions import ValidationError

from .models import BatchProcessing
from .models import LLMModel


class BatchProcessingForm(forms.ModelForm):
    model = forms.ModelChoiceField(
        queryset=LLMModel.objects.filter(is_active=True),
        help_text="Select the LLM model to use for processing",
    )
    essay_field_name = forms.CharField(
        initial="Essay",
        help_text="Name of the column containing essays in the Excel file",
    )
    input_file = forms.FileField(
        help_text="Upload an Excel file (.xlsx) containing essays to process",
    )

    class Meta:
        model = BatchProcessing
        fields = ["model", "essay_field_name", "input_file"]

    def clean_input_file(self):
        file = self.cleaned_data["input_file"]
        if not file.name.endswith(".xlsx"):
            msg = "Only Excel (.xlsx) files are allowed"
            raise ValidationError(msg)

        try:
            df_data = pd.read_excel(file)
            essay_field = self.cleaned_data.get("essay_field_name", "Essay")
            if essay_field not in df_data.columns:
                msg = (
                    f"Column '{essay_field}' not found in the Excel file. "
                    f"Available columns: {', '.join(df_data.columns)}",
                )
                raise ValidationError(msg)
        except (ValueError, TypeError) as e:
            msg = f"Error reading Excel file: {e!s}"
            raise ValidationError(msg) from e

        file.seek(0)  # Reset file pointer
        return file

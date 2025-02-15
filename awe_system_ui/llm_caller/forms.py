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
    essay_topic_field_name = forms.CharField(
        initial="Essay Topic",
        help_text="Name of the column containing essay topics in the Excel file",
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
        fields = ["model", "essay_field_name", "essay_topic_field_name"]

    def clean_input_file(self):
        file = self.cleaned_data["input_file"]
        if not file.name.endswith(".xlsx"):
            msg = "Only Excel (.xlsx) files are allowed"
            raise ValidationError(msg)

        try:
            df_data = pd.read_excel(file)
            required_columns = [
                ("essay_field_name", "Essay"),
                ("essay_topic_field_name", "Essay Topic"),
            ]

            for form_field, default_name in required_columns:
                column_name = self.cleaned_data.get(form_field, default_name)
                if column_name not in df_data.columns:
                    msg = (
                        f"Column '{column_name}' not found in the Excel file. "
                        f"Available columns: {', '.join(df_data.columns)}",
                    )
                    raise ValidationError(msg)

            # Store the DataFrame in the form for later use
            self.cleaned_data["df_data"] = df_data
        except (ValueError, TypeError) as e:
            msg = f"Error reading Excel file: {e!s}"
            raise ValidationError(msg) from e

        return file

from django import forms


class MediumsForm(forms.Form):
    csv_input = forms.CharField(required=True, widget=forms.Textarea)

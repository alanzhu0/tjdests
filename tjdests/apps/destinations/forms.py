# Filter Form
from django import forms

class FilterForm(forms.Form):
    gpa_min = forms.FloatField(
        required=False, 
        label="Min GPA",
        widget=forms.NumberInput(attrs={"placeholder": "Min GPA", "min": 0, "max": 5, "step": 0.01})
    )
    gpa_max = forms.FloatField(
        required=False, 
        label="Max GPA",
        widget=forms.NumberInput(attrs={"placeholder": "Max GPA", "min": 0, "max": 5, "step": 0.01})
    )
    college = forms.ChoiceField(
        required=False,
        label="College",
        choices=[],  
        widget=forms.Select(attrs={"data-live-search": "true"})
    )
    decision = forms.MultipleChoiceField(
        required=False,
        label="Decision Type",
        choices=[],  
        widget=forms.CheckboxSelectMultiple
    )
    admission = forms.MultipleChoiceField(
        required=False,
        label="Admission Type",
        choices=[],   
        widget=forms.CheckboxSelectMultiple
    )
    sat_min = forms.IntegerField(
        required=False,
        label="SAT Min Score",
        widget=forms.NumberInput(attrs={"placeholder": "Min SAT", "min": 0, "max": 1600})
    )
    sat_max = forms.IntegerField(
        required=False,
        label="SAT Max Score",
        widget=forms.NumberInput(attrs={"placeholder": "Max SAT", "min": 0, "max": 1600})
    )
    act_min = forms.IntegerField(
        required=False,
        label="ACT Min Score",
        widget=forms.NumberInput(attrs={"placeholder": "Min ACT", "min": 0, "max": 36})
    )
    act_max = forms.IntegerField(
        required=False,
        label="ACT Max Score",
        widget=forms.NumberInput(attrs={"placeholder": "Max ACT", "min": 0, "max": 36})
    )
        
    def __init__(self, *args, **kwargs):
            colleges = kwargs.pop('colleges', [])
            decisions = kwargs.pop('decisions', [])
            admissions = kwargs.pop('admissions', [])
            super().__init__(*args, **kwargs)
            
            # Populate the choices dynamically
            self.fields['college'].choices =  [("", "Select a College")] + [(college.id, college.name) for college in colleges]
            self.fields['decision'].choices = [(decision.id, decision.name) for decision in decisions]
            self.fields['admission'].choices = [(admission.id, admission.name) for admission in admissions]
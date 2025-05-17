from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from . import models
from .models import Applications

#for admin
class AdminSignupForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']

#for student related form
class StudentUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
class StudentExtraForm(forms.ModelForm):
    class Meta:
        model=models.StudentExtra
        fields=['personal_id','email','status']        

class SchemeForm(forms.ModelForm):
    class Meta:
        model=models.Scheme
        fields = [
            'name',
            'description',
            'eligibility_criteria',
            'application_deadline',
            'grade',
            'year_of_scholarship',
            'documents_required',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'eligibility_criteria': forms.Textarea(attrs={'rows': 4}),
            'documents_required': forms.Textarea(attrs={'rows': 3}),
            
        }


#for student appliprocess form
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Applications
        fields = ['full_name', 'gender', 'date_of_birth', 'id_number', 'location', 'sub_location', 'email', 'phone',
                  'guardian_id', 'guardian_first_name', 'guardian_occupation', 'guardian_income', 'guardian_kra', 'guardian_contact', 
                  'institution_type','institution_name_undergraduate', 'course', 'reg_no', 'annual_program_cost',
                  'year_of_completion', 'current_year', 'amount_family_can_raise_undergraduate', 'amount_requested_undergraduate',
                  'institution_name_primary','nemis_number_primary','amount_family_can_raise_primary','amount_requested_primary','grade',
                  'institution_name_secondary','form','nemis_secondary','amount_family_can_raise_secondary','amount_requested_secondary',
                  'bank_name', 'branch_name', 'account_number', 'personal_id', 'fee_structure', 'school_transcript', 'other_document'
                  ]


    def validate_positive(self, field_name):
        """Helper function to check if a value is positive"""
        value = self.cleaned_data.get(field_name)
        if value is not None and value < 0:
            raise ValidationError(f"{field_name.replace('_', ' ').capitalize()} must be a positive value.")
        return value

    def clean_id_number(self):
        id_number = self.cleaned_data.get("id_number")
        if not id_number.isdigit() or int(id_number) <= 0:
            raise ValidationError("ID number must be a positive number.")
        return id_number

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit() or int(phone) <= 0:
            raise ValidationError("Phone number must be a positive number.")
        return phone

    def clean_guardian_id(self):
        guardian_id = self.cleaned_data.get("guardian_id")
        if not guardian_id.isdigit() or int(guardian_id) <= 0:
            raise ValidationError("Guardian ID must be a positive number.")
        return guardian_id

    def clean_guardian_income(self):
        return self.validate_positive("guardian_income")

    def clean_guardian_contact(self):
        guardian_contact = self.cleaned_data.get("guardian_contact")
        if guardian_contact and (not guardian_contact.isdigit() or int(guardian_contact) <= 0):
            raise ValidationError("Guardian contact must be a positive number.")
        return guardian_contact

    def clean_annual_program_cost(self):
        return self.validate_positive("annual_program_cost")

    def clean_current_year(self):
        current_year = self.cleaned_data.get("current_year")
        if current_year and (not current_year.isdigit() or int(current_year) <= 0):
            raise ValidationError("Current year must be a positive number.")
        return current_year

    def clean_amount_family_can_raise_undergraduate(self):
        return self.validate_positive("amount_family_can_raise_undergraduate")

    def clean_amount_requested_undergraduate(self):
        return self.validate_positive("amount_requested_undergraduate")

    def clean_amount_family_can_raise_primary(self):
        return self.validate_positive("amount_family_can_raise_primary")

    def clean_amount_requested_primary(self):
        return self.validate_positive("amount_requested_primary")

    def clean_amount_family_can_raise_secondary(self):
        return self.validate_positive("amount_family_can_raise_secondary")

    def clean_amount_requested_secondary(self):
        return self.validate_positive("amount_requested_secondary")              
       
 #######student notice form       
class NoticeForm(forms.ModelForm):
    class Meta:
        model=models.Notice
        fields='__all__'



#####disburse admin
class DisbursementForm(forms.ModelForm):
    class Meta:
        model = models.Disbursement
        fields = ['application', 'amount']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount < 1:
            raise ValidationError("disbursement amount must be positive")
        return amount

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['application'].queryset = Applications.objects.filter(status="Approved")



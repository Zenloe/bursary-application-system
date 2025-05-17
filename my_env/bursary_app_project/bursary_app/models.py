from django.db import models 
from django.contrib.auth.models import User  
from datetime import date

# Create your models here.

class StudentExtra(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    personal_id = models.CharField(max_length=10)
    email = models.EmailField(default='a@gmail.com')
    status=models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name


class Scheme(models.Model):
    GRADE_CHOICES = [
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    eligibility_criteria = models.TextField(default='')
    application_deadline = models.DateField(default=date.today)
    grade = models.CharField(max_length=15, choices=GRADE_CHOICES, default='undergraduate')
    year_of_scholarship = models.PositiveIntegerField(default=2025)
    documents_required = models.TextField(default='', help_text="List documents separated by commas")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name
    


class BursaryFund(models.Model):
    total_fund = models.DecimalField(max_digits=12, decimal_places=2, default=500000.00)
    used_fund = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    @property
    def remaining_fund(self):
        return self.total_fund - self.used_fund



class Applications(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Disbursed", "Disbursed"),
        ("Flagged", "Flagged"),
    ]
    student = models.ForeignKey(StudentExtra, on_delete=models.CASCADE)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE) 
    # Step 1: Applicant Details
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    id_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    sub_location = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    # Step 2: Guardian Details
    guardian_id = models.CharField(max_length=20)
    guardian_first_name = models.CharField(max_length=255)
    guardian_occupation = models.CharField(max_length=255, default='occupation')
    guardian_income = models.DecimalField(max_digits=10, decimal_places=2 ,default=0)
    guardian_kra = models.CharField(max_length=11, null=True)
    guardian_contact = models.CharField(max_length=15, null=True)

    # Step 3: School Details (Dynamic)
    INSTITUTION_TYPES = (
        ('undergraduate', 'Undergraduate'),
        ('secondary', 'Secondary'),
        ('primary', 'Primary'),
    )
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES)

    # Undergraduate specific fields
    institution_name_undergraduate = models.CharField(max_length=255, blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)
    reg_no = models.CharField(max_length=20, blank=True, null=True)
    annual_program_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    year_of_completion = models.CharField(max_length=4, blank=True, null=True) 
    current_year = models.CharField(max_length=4, blank=True, null=True)
    amount_family_can_raise_undergraduate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_requested_undergraduate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)

    # Primary specific fields
    institution_name_primary = models.CharField(max_length=255, blank=True, null=True)
    nemis_number_primary = models.CharField(max_length=20, blank=True, null=True)
    amount_family_can_raise_primary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_requested_primary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    grade = models.CharField(max_length=20, blank=True, null=True)

    # Secondary specific fields
    institution_name_secondary = models.CharField(max_length=255, blank=True, null=True)
    form = models.CharField(max_length=20, blank=True, null=True)
    nemis_secondary = models.CharField(max_length=20, blank=True, null=True)
    amount_family_can_raise_secondary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_requested_secondary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Step 4: Bank Details
    bank_name = models.CharField(max_length=255)
    branch_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20)

    # Step 5: Documents
    personal_id = models.FileField(upload_to='documents/')
    fee_structure = models.FileField(upload_to='documents/')
    school_transcript = models.FileField(upload_to='documents/')
    other_document = models.FileField(upload_to='documents/')

        #ocr extracted text
    extracted_id_name = models.CharField(max_length=255, blank=True, null=True)
    extracted_institution_name = models.CharField(max_length=255, blank=True, null=True)

    
    status = models.CharField(max_length=50, default="Pending", choices=STATUS_CHOICES)
    submission_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)


 

    def __str__(self):
        return f"{self.full_name} - {self.scheme} - {self.status}"
         

#disbursement related logiccccccccccccccccccccccccc

class Disbursement(models.Model):
    application = models.OneToOneField(Applications, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_disbursed = models.DateTimeField(auto_now_add=True)


class Notice(models.Model):
    date=models.DateField(auto_now=True)
    by=models.CharField(max_length=20,null=True,default='bursary')
    message=models.CharField(max_length=500)
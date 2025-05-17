
from django.shortcuts import render,redirect,reverse
from . import forms,models
from .forms import SchemeForm, ApplicationForm, NoticeForm,DisbursementForm
from .models import Applications, Notice, Scheme, StudentExtra,BursaryFund
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout, update_session_auth_hash
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
import csv
from .utils import extract_text_from_image
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def home_view(request):
    return render(request, 'bursary/index.html')
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'bursary/index.html')  

def about_view(request):
    return render(request, 'bursary/about.html')


def adminclick_view(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request,'bursary/adminclick.html') 

def studentclick_view(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'bursary/studentclick.html') 


def admin_signup_view(request):
    form=forms.AdminSignupForm()
    if request.method=='POST':
        form=forms.AdminSignupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()

            my_admin_group, created = Group.objects.get_or_create(name='ADMIN')
            my_admin_group.user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request,'bursary/adminsignup.html',{'form':form})



def student_signup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_student_group, created = Group.objects.get_or_create(name='STUDENT')
            my_student_group.user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request,'bursary/studentsignup.html',context=mydict)



def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


       

def afterlogin_view(request):
    if not request.user.is_authenticated:
        return redirect('')
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_student(request.user):
        return redirect('student-dashboard') 
    else:
        return render(request,'bursary/index.html',{'error': 'invalid user role'})    
  





#for dashboard of adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    #application count
    fund, created = BursaryFund.objects.get_or_create(
        id=1, 
        defaults={"total_fund": 500000, "used_fund": 0}
    )
    utilization_percentage = (fund.used_fund / fund.total_fund) * 100 if fund.total_fund > 0 else 0

    total_applications = models.Applications.objects.count()
    approved_applications = models.Applications.objects.filter(status="approved").count()
    pending_applications = models.Applications.objects.filter(status="pending").count()
    disbursed_applications = models.Applications.objects.filter(status="disbursed").count()
    flagged_applications = Applications.objects.filter(status="Flagged").count()
    undergraduate_count = Applications.objects.filter(institution_type="undergraduate").count()
    secondary_count = Applications.objects.filter(institution_type="secondary").count()
    primary_count = Applications.objects.filter(institution_type="primary").count()
    
    applications = Applications.objects.all() 
    
    total_scheme = models.Scheme.objects.count()
    notice=models.Notice.objects.all()

    mydict = {
        'total_applications': total_applications,
        'approved_applications': approved_applications,
        'pending_applications': pending_applications,
        'total_scheme': total_scheme,
        'notice':notice,
        'applications': applications,  
        'disbursed_applications':disbursed_applications,
        'flagged_applications':flagged_applications,
        "total_fund": fund.total_fund,
        "used_fund": fund.used_fund,
        "utilization_percentage": utilization_percentage,
        "undergraduate_count": undergraduate_count,
        "secondary_count": secondary_count,
        "primary_count": primary_count,
       

    }
    return render(request,'bursary/admin_dashboard.html', context=mydict)




#############admin verifiy documents
def verify_application(application):  
    student_name = application.full_name.lower().strip()
    if application.institution_type == "primary":
        school_name = application.institution_name_primary
    elif application.institution_type == "secondary":
        school_name = application.institution_name_secondary
    else: 
        school_name = application.institution_name_undergraduate
    
    school_name = school_name.lower().strip() if school_name else ""
    print(f"Verifying application for {student_name} at {school_name}")

    extracted_id_text = extract_text_from_image(application.personal_id.path).lower().strip()
    extracted_school_text = extract_text_from_image(application.school_transcript.path).lower().strip()

    print(f"Extracted ID text: {extracted_id_text}")
    print(f"Extracted school text: {extracted_school_text}")

    name_match_score = fuzz.partial_ratio(student_name, extracted_id_text)
    school_match_score = fuzz.partial_ratio(school_name, extracted_school_text)

    MATCH_THRESHOLD = 80  

    application.extracted_id_name = extracted_id_text
    application.extracted_school_name = extracted_school_text

    if name_match_score > MATCH_THRESHOLD and school_match_score > MATCH_THRESHOLD:
        application.status = "Approved"
    else:
        application.status = "Flagged"

    application.save()




###########all appplications adminnnnnnnnnnnnnnnn
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def all_applications_view(request):
    students_applications = Applications.objects.all()
    return render(request, 'bursary/admin_category_applications.html', {'students_applications': students_applications})


######### for admin under,sec and pri applications tabs
def institution_applications(request, institution_type):
    applications = Applications.objects.filter(institution_type=institution_type)
    return render(request, 'bursary/admin_underprisec_applications.html', {
        'applications': applications,
        'institution_type': institution_type
    })


# appppppppppppppppplications admnin
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_application(request, app_id):
    application = get_object_or_404(Applications, id=app_id)
    application.status = "Approved"
    application.save()
    return HttpResponseRedirect(reverse('admin-dashboard'))


def approved_applications(request):
    approved_students = Applications.objects.filter(status="Approved")
    return render(request, 'bursary/admin_approved_applications.html', {'approved_students': approved_students})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_pending_applications_view(request):
    flagged_applications = Applications.objects.filter(status="Flagged")
    context = {
        'flagged_applications': flagged_applications
    }
    return render(request,'bursary/admin_flaggedapplications.html', context)
def review_application_view(request, application_id):
    application = get_object_or_404(Applications, id=application_id)
    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision == 'approve':
            application.status = 'Approved'
        elif decision == 'reject':
            if application.status == 'Flagged':
                application.status = 'Not Approved'  
            else:
                application.status = 'rejected'  
        application.save()
        return redirect('admin_pending_applications')
    return render(request, 'bursary/admin_review_application.html', {'application': application})



#disbursementttttttttttttttttttttttttttttttttttttttttt admin
def disburse_funds(request):
    fund = BursaryFund.objects.first()  # Assume a single fund record
    if not fund:
        messages.error(request, "No bursary fund available.")
        return redirect("admin-dashboard")

    if request.method == "POST":
        form = DisbursementForm(request.POST)
        if form.is_valid():
            disbursement = form.save(commit=False)
            application = disbursement.application

            if application.status == "Disbursed":
                messages.error(request, "This application has already been disbursed.")
                return redirect("disburse-funds")

            if application.institution_type == "primary":
                requested_amount = application.amount_requested_primary
            elif application.institution_type == "secondary":
                requested_amount = application.amount_requested_secondary
            elif application.institution_type == "undergraduate":
                requested_amount = application.amount_requested_undergraduate
            else:
                messages.error(request, "Invalid institution type.")
                return redirect("disburse-funds")

            if requested_amount is None:
                messages.error(request, "Requested amount not specified for this application.")
                return redirect("disburse-funds")

            if disbursement.amount > requested_amount:
                messages.error(request, f"Amount cannot exceed the requested amount ({requested_amount}).")
                return redirect("disburse-funds")

            if disbursement.amount > fund.remaining_fund:
                messages.error(request, "Insufficient funds available.")
                return redirect("disburse-funds")

            fund.used_fund += disbursement.amount
            
            fund.save()

            application.status = "Disbursed"
            application.save()

            disbursement.save()

            messages.success(request, "Funds successfully disbursed.")
            return redirect("disburse-funds")
        
        else:
            messages.error(request, "corect errors ")

    else:
        form = DisbursementForm()

    return render(request, "bursary/disbursefund.html", {"form": form, "fund": fund})

#admin download reporttttttttttt
def export_fund_data(request):
    fund, created = BursaryFund.objects.get_or_create(
        id=1, 
        defaults={"total_fund": 500000, "used_fund": 0}
    )
    used_fund = fund.used_fund
    total_fund = fund.total_fund
    utilization_percentage = (fund.used_fund / fund.total_fund) * 100 if fund.total_fund > 0 else 0
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fund_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["used funds", "remaining funds","utilization %"])
    writer.writerow([used_fund, total_fund-used_fund, utilization_percentage])

    return response




# for scheme by adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_scheme_view(request):
    return render(request,'bursary/admin_scheme.html')
    
       
 #for addscheme by adminnnnnnnnnnnnnnnnn
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_scheme_view(request, scheme_id=None):
    scheme = None
    if scheme_id:  
        scheme = get_object_or_404(Scheme, id=scheme_id)
        print("Editing Scheme:", scheme.name) 

    if request.method == 'POST':
        form = SchemeForm(request.POST, instance=scheme)  
        if form.is_valid():
            form.save()
            return redirect('scheme_list')
        else:
            print("Form errors:", form.errors)  
    else:
        form = SchemeForm(instance=scheme)  
        print("Prepopulated form data:", form.initial)  

    return render(request, 'bursary/admin_scheme.html', {'form': form, 'scheme': scheme})

def scheme_list(request):
    schemes = Scheme.objects.all()  
    return render(request, 'bursary/admin_scheme_list.html', {'schemes': schemes})


def delete_scheme(request, scheme_id):
    scheme = get_object_or_404(Scheme, id=scheme_id)
    scheme.delete()
    return redirect('scheme_list')  




#admin manage usersssssssssssssssssssssssssssssss
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_manage_users(request):
    users = Applications.objects.all()
    return render(request, 'bursary/admin_manageUsers.html',{'users':users})


#admin delete users
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_user(request, id_number):
    user = get_object_or_404(Applications, id_number=id_number)
    if user:
        user.delete()
    return redirect('admin-manage-users')    
    

# for profile by adminnnnnnnnnnnnnnnnnnnnnnnn

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_profile_view(request):
    return render(request,'bursary/admin_profile.html')


# for settings by adminnnnnnnnnnnnnnnn
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_settings_view(request):
    return render(request,'bursary/admin_settings.html')


#notice admnnnnnnnnnnnnnnnnnnnn
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_notice_view(request):
    form=forms.NoticeForm()
    if request.method=='POST':
        form=forms.NoticeForm(request.POST)
        if form.is_valid():
            form=form.save(commit=False)
            form.by=request.user.first_name
            form.save()
            return redirect('admin-dashboard')
    return render(request, 'bursary/admin_notice.html',{'form':form})    



#FOR STUDENT AFTER THEIR Loginnnnnnnnnnnnnnnnnnnnn logggggggggggggggggggggggic
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    student = request.user.studentextra 
    total_scheme = models.Scheme.objects.count()

    student_applications = models.Applications.objects.filter(student=student)

    total_applications = student_applications.count()
    approved_count = student_applications.filter(status='Approved').count()
    dispersed_count = student_applications.filter(status='Disbursed').count()
    notice=models.Notice.objects.all()

    mystudict = {
        'total_scheme': total_scheme,
        'student_applications': student_applications,
        'approved_count': approved_count,
        'dispersed_count': dispersed_count,
        'total_applications':total_applications,
        'notice':notice,
    }

    return render(request, 'bursary/student_dashboard.html', context=mystudict)

#student applicationryyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def application_form(request, scheme_id):
    print(f"Received scheme_id: {scheme_id}")  

    
    try:
        scheme = Scheme.objects.get(id=scheme_id)
        print(f"Fetched scheme: {scheme}")  
    except Scheme.DoesNotExist:
        print("Scheme not found")  
        return render(request, 'error.html', {'error': 'Scheme not found'})

    if request.method == "POST":
        print("Form submission detected") 
        form = ApplicationForm(request.POST, request.FILES)
        print(f"Form data received: {request.POST}") 

        if form.is_valid():
            print("Form is valid")  
            application = form.save(commit=False) 
            
           
            try:
                student = StudentExtra.objects.get(user=request.user)
                application.student = student
                print(f"Student found: {student}")  
            except StudentExtra.DoesNotExist:
                print("Student profile not found") 
                return render(request, 'error.html', {'error': 'Student profile not found'})

            application.scheme = scheme

            existing_application = Applications.objects.filter(student=student, scheme=scheme).first()
            if existing_application:
                print("Student has already applied for this scheme")  
                form.add_error(None, "You have already applied for this scheme.")
                return render(request, "bursary/student_application.html", {
                    "form": form,
                    "scheme": scheme,
                    "error_message": "You have already applied for this scheme."
                })

           
            application.status = "Pending"  
            application.save()
            print(f"Application saved: {application}")  

            # Trigger OCR verification**
            verify_application(application) 
            print("OCR verification triggered")  

            return redirect('application_success')  
        else:
            print("Form is invalid, errors:", form.errors) 

    else:
        print("Rendering application form page")  
        form = ApplicationForm()

    return render(request, "bursary/student_application.html", {
        "form": form,
        "scheme": scheme
    })



#for student application success messageeeeeeeeeeeeeeeeeeeeeee
def application_success(request):
    return render(request, 'bursary/student_application_success.html')


def student_application_history(request):
    
    try:
        student = request.user.studentextra  
        applications = Applications.objects.filter(student=student)
    except StudentExtra.DoesNotExist:
        applications = []

    return render(request, 'bursary/student_application_history.html', {'applications': applications})


def application_detail(request, application_id):
    print(f"Received application_id: {application_id} (Type: {type(application_id)})")  
    application = get_object_or_404(Applications, id=application_id)

    return render(request, 'bursary/student_application_details.html', {'application': application})



# for student view scheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeme
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_scheme_view(request):
    schemes = Scheme.objects.all()

    return render(request,'bursary/student_view_scheme.html',{'schemes': schemes}) 
    


@login_required 
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            return redirect('student-dashboard') 
        else:
            messages.error(request, 'Please correct the error below.')

    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'bursary/student_changepassword.html', {'form': form})




# for    the end     pprofiles and logoutsssssssssssssssssssssssssssss

#logout
def logout_view(request):
    logout(request)
    return redirect('home')
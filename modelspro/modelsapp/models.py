from django.db import models
import datetime

# Create your models here.


class Address(models.Model):
    H_No = models.CharField(max_length=30)
    Line1 = models.CharField(max_length=30)
    street = models.CharField(max_length=30)
    colony = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    pin = models.IntegerField()

class JobTitle(models.Model):
    title = models.CharField(max_length=30)

class Department(models.Model):
    dep_name = models.CharField(max_length=30)

class Supervisor(models.Model):
    sup_id = models.IntegerField()

class Contact(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    sur_name = models.CharField(max_length=30)
    login_name = models.CharField(max_length=30,default="suser1")
    email = models.EmailField()
    emp_id = models.IntegerField()
    supervisor = models.ForeignKey(Supervisor)
    department = models.ForeignKey(Department)
    job_title = models.ForeignKey(JobTitle)
    phone = models.IntegerField()
#   picture = models.CharField(max_length=30)
    picture = models.FileField(upload_to='tmp/')
    address = models.OneToOneField(Address)

class SkillTitle(models.Model):
    skill_title = models.CharField(max_length=30)
    
class Skill(models.Model):
    skill_name = models.CharField(max_length=30)
    exp_years = models.IntegerField()
    exp_level = models.IntegerField()
    contact = models.ManyToManyField(Contact)

class Leave(models.Model):
    requester = models.ForeignKey(Contact)
    app_id = models.IntegerField(default=0)
    req_date = models.DateField(blank=False, default=datetime.datetime.now)
    app_date = models.DateField(blank=False, default=datetime.datetime.now)
    from_date = models.DateField(blank=False, default=datetime.datetime.now)
    to_date = models.DateField(blank=False, default=datetime.datetime.now)
    count = models.IntegerField(default=0)
    state = models.IntegerField(default=0)
    type = models.IntegerField(default=0)
    req_comment = models.CharField(max_length=250, default='-')
    app_comment = models.CharField(max_length=250, default='-')

class Holiday(models.Model):
    h_date = models.DateField()
    holiday_name = models.CharField(max_length=50)

class LeaveBalance(models.Model):
    contact = models.OneToOneField(Contact)
    sick_leave_balance = models.IntegerField(default=0)
    earned_leave_balance = models.IntegerField(default=0)

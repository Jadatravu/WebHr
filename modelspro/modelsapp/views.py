from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf

from modelsapp.models import Contact
from modelsapp.forms import ContactForm
from modelsapp.models import JobTitle
from modelsapp.forms import JobTitleForm

from modelsapp.models import Department
from modelsapp.forms import DepartmentForm

from modelsapp.models import Supervisor
from modelsapp.forms import SupervisorForm
from modelsapp.forms import ViewContactForm

from modelsapp.models import Address
from modelsapp.forms import ESearchForm

from modelsapp.models import SkillTitle
from modelsapp.forms import SkillTitleForm

from modelsapp.models import Skill

from modelsapp.models import Holiday

from modelsapp.models import LeaveBalance

from modelsapp.models import Leave

import datetime

from django.contrib.auth import (REDIRECT_FIELD_NAME, login as auth_login,
    logout as auth_logout, get_user_model, update_session_auth_hash)
from django.contrib.sites.shortcuts import get_current_site
from django.template.response import TemplateResponse

from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm

from django.contrib.auth import authenticate, logout
from django.contrib import auth

from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)


# Create your views here.
def approveleave(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("log 0 =>request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    con_list = Contact.objects.filter(login_name=request.user.username)
    logger.debug ("con_list len  %d"%len(con_list))
    lea_list=[]
    if (len(con_list) > 0):
        lea_list = Leave.objects.filter(app_id=con_list[0].id)

    logger.debug ("lea_list len  %d"%len(lea_list))
    return render_to_response(
                      'approveleave.html',
                       {'user':request.user,'leave_list':lea_list},
                       context_instance=RequestContext(request)
                     )#
    pass

def approveleave_form(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("log 0 =>request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    if request.method == 'POST':
        comment = request.POST['comment']
        leave_id = request.POST['leave_id']
        lea = Leave.objects.get(id=leave_id)
        lea.app_date=datetime.datetime.now()
        lea.app_comment=comment
        lea.state=1 #approved
        lea.save()
        logger.debug("leave state : %d"%lea.state)
        logger.debug("leave app comment : %s"%lea.app_comment)
        return render_to_response(
                      'approveleaveform.html',
                       {'user':request.user,'leave':lea},
                       context_instance=RequestContext(request)
                     )#

def approveleaveform(request,leave_id):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("log 0 =>request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    lea = Leave.objects.get(id=leave_id)
    return render_to_response(
                      'approveleaveform.html',
                       {'user':request.user,'leave':lea},
                       context_instance=RequestContext(request)
                     )#


def applyleaveform(request):
    #if (request.user.is_authenticated() == False):
    #if request.user.is_authenticated() and request.user.is_superuser:
    if request.user.is_authenticated():
        logger.debug ("log 0 =>request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    logger.debug("this is  apply leaves form")
    message=""
    if request.method == 'POST':
        fm_date = request.POST['datevalue']
        t_date = request.POST['datevalue1']
        comment = request.POST['comment']
        con_id = request.POST['contact_id']
        tpe = request.POST['type']
        logger.debug("from date => %s"%fm_date)
        logger.debug("to date => %s"%t_date)
        logger.debug("comment => %s"%comment)
        from_date_list = str(fm_date).split('/')
        to_date_list = str(t_date).split('/')
        if (len(from_date_list) > 1 and len(to_date_list) > 1):
             f_date = datetime.date(int(from_date_list[2]),int(from_date_list[0]),int(from_date_list[1]))
             t_date = datetime.date(int(to_date_list[2]),int(to_date_list[0]),int(to_date_list[1]))
             d=f_date
             no_applying_leaves = 0
             #calculate no_of_days_leave considering holidays,earlier applied leaves
             time_delta = datetime.timedelta(1)
             while ((t_date -d) > datetime.timedelta(0)):
                 is_h_day = 0
                 h_day_list=Holiday.objects.all()
                 #check d is holiday
                 for hd in h_day_list:
                     if hd.h_date == d:
                        is_h_day=1
                 #check d is a saturday/sunday
                 if is_h_day == 0:
                     if (d.weekday() == 5 or d.weekday() ==6) :
                        is_h_day=1
                 #check d is already applied leave day 
                 if is_h_day == 0:
                    contact=Contact.objects.get(id=con_id)
                    leave_list = Leave.objects.filter(requester=contact)
                    for leave in leave_list:
                        if leave.count == 1:
                           if leave.from_date == d:
                               is_h_day=1
                        elif leave.count > 1:
                            l_day = leave.from_date
                            while (l_day < leave.to_date):
                                if l_day == d:
                                    is_h_day=1
                                l_day = l_day + time_delta
                 if is_h_day == 0:
                     no_applying_leaves += 1
                 d=d+time_delta
             #if the leave balance is sufficient update leave_balance_table,Leave Table
             logger.debug("no_applying leaves => %d"%no_applying_leaves)
             cont=Contact.objects.get(id=con_id)
             le_balance=LeaveBalance.objects.filter(contact=cont)
             logger.debug(le_balance[0].sick_leave_balance)
             logger.debug(le_balance[0].earned_leave_balance)
             logger.debug("type => %d"%int(tpe))
             if (int(tpe) == 0):
                if ((no_applying_leaves > 0) and ( le_balance[0].sick_leave_balance - no_applying_leaves > -1)):
                     logger.debug("sick no_applying leaves => %d"%no_applying_leaves)
                     logger.debug("app_id => %d"%cont.supervisor.sup_id)
                     logger.debug("app_id => %d"%cont.supervisor_id)
                     apply_leave = Leave(requester=cont, app_id=cont.supervisor.sup_id,from_date=f_date,to_date=t_date,count=no_applying_leaves,state=0,type=tpe,req_comment=comment,app_comment="-")
                     apply_leave.save()
                     #le_balance[0].sick_leave_balance = le_balance[0].sick_leave_balance - no_applying_leaves
                     sick_leave_bal = le_balance[0].sick_leave_balance 
                     sick_leave_bal = sick_leave_bal - no_applying_leaves
                     le_balance[0].sick_leave_balance = sick_leave_bal
                     logger.debug("sick_leave_ balance %d"%le_balance[0].sick_leave_balance)
                     logger.debug("sick_leave_ bal %d"%sick_leave_bal)
                     leave_id = le_balance[0].id
                     le_bal=LeaveBalance.objects.get(id=leave_id)
                     le_bal.sick_leave_balance = sick_leave_bal
                     le_bal.save()
                     logger.debug("sick_leave_ balance %d"%le_balance[0].sick_leave_balance)
                     logger.debug("sick_leave_ balance %d"%le_bal.sick_leave_balance)
                if (( le_balance[0].sick_leave_balance - no_applying_leaves < 0)):
                    message = "Insufficient Leave Balance"
             elif (int(tpe) == 1):
                if ((no_applying_leaves > 0) and ( le_balance[0].earned_leave_balance - no_applying_leaves > -1)):
                     logger.debug("earned no_applying leaves => %d"%no_applying_leaves)
                     apply_leave = Leave(requester=cont, app_id=cont.supervisor_id,from_date=f_date,to_date=t_date,count=no_applying_leaves,state=0,type=tpe,req_comment=comment,app_comment="-")
                     apply_leave.save()
                     earned_leave_bal = le_balance[0].earned_leave_balance 
                     earned_leave_bal = earned_leave_bal -  no_applying_leaves
                     leave_id = le_balance[0].id
                     le_bal=LeaveBalance.objects.get(id=leave_id)
                     le_bal.earned_leave_balance = earned_leave_bal
                     le_bal.save()
                     logger.debug("earned_leave balance %d"%le_bal.earned_leave_balance)
                if (( le_balance[0].earned_leave_balance - no_applying_leaves < 0)):
                    message = "Insufficient Leave Balance"
                 
             #send error message if the leave balance is not sufficient
    leave_balance_list=[]
    contacts_list = Contact.objects.filter(login_name=request.user.username) 
    for con in contacts_list:
       logger.debug("id => %d"%con.id)
       le_bl=LeaveBalance.objects.filter(contact=con)
       leave_balance_list.append(le_bl[0])
    logger.debug("leave_balance_list => %d"%len(leave_balance_list))
    logger.debug("user => %s"%request.user.username)
    logger.debug("len => %d"%len(contacts_list))
    return render_to_response(
                      'applyleave.html',
                       {'user':request.user,'contacts_list':contacts_list, 'msg':message,'leave_bal_list':leave_balance_list},
                       context_instance=RequestContext(request)
                     )#

def releaseleaves(request):
    sick_leave_add = 1
    earned_leave_add = 1
    #if (request.user.is_authenticated() == False):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("log 0 =>request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    logger.debug("this is  release leaves form")
    contacts_list = Contact.objects.all()
    for con in contacts_list:
       le_balance=LeaveBalance.objects.filter(contact=con)
       if (len(le_balance) > 0):
            le_balance[0].sick_leave_balance += sick_leave_add
            le_balance[0].earned_leave_balance +=earned_leave_add 
            le_balance[0].save()
       else:
          le_bal = LeaveBalance(contact=con, sick_leave_balance=sick_leave_add, earned_leave_balance=earned_leave_add)
          le_bal.save()
    le_bal_list=LeaveBalance.objects.all()
    logger.debug ("h_len %d "%len(le_bal_list))
    return render_to_response(
                      'releaseleaves.html',
                       {'leave_balance_list': le_bal_list, 'user':request.user},
                       context_instance=RequestContext(request)
                     )#

def addholidayform(request):
    #if (request.user.is_authenticated() == False):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("log 0 =>request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    logger.debug("this is  add holiday form")
    if request.method == 'POST':
        da_value = request.POST['datevalue']
        h_name = request.POST['h_name']
        logger.debug ("h_date %s "%da_value)
        da_value_list = da_value.split('/')
        holiday_date=da_value_list[2]+str('-')+da_value_list[0]+str('-')+da_value_list[1]
        h_day=Holiday(holiday_name=h_name,h_date=holiday_date)
        h_day.save()
        return HttpResponseRedirect(reverse('modelsapp.views.addholidayform'))
    holidays_list=Holiday.objects.filter(h_date__year=datetime.datetime.now().year)
    #holidays_list=[]
    logger.debug ("h_len %d "%len(holidays_list))
    return render_to_response(
                      'addholiday.html',
                       {'holidays': holidays_list, 'user':request.user},
                       context_instance=RequestContext(request)
                     )#

def skillcontactaddform(request):
    #if (request.user.is_authenticated() == False):
    #if request.user.is_authenticated() and request.user.is_superuser:
    if request.user.is_authenticated():
        logger.debug ("log 0 =>request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    logger.debug("this is skill title contact add form")
    if request.method == 'POST':
        exper_years1 = request.POST['years']
        skill_title1 = request.POST['title']
        exper_level1 = request.POST['exper']
        con_id = request.POST['con_id']
        sk=Skill(skill_name=skill_title1,exp_years=exper_years1,exp_level=exper_years1)
        sk.save()
        contact=Contact.objects.get(id=con_id)
        """
        contacts_list=Contact.objects.filter(login_name__contains=request.user)
        if( len(contacts_list) > 0):
            sk.contact.add(contacts_list[0])
        """
        sk.contact.add(contact)
        return HttpResponseRedirect(reverse('modelsapp.views.skillcontactaddform'))
    else:
        logger.debug (" log 1 =>request user %s is authenticated"%request.user.username)
        contacts_list=Contact.objects.filter(login_name__contains=request.user.username)
        logger.debug (" log 1 =>contacts_list len %d is authenticated"%len(contacts_list))
        skill_contact_list={}
        for ct in contacts_list:
           skill_contact_list[ct]=ct.skill_set.all()
           
        if( len(contacts_list) > 0):
             skill_list=contacts_list[0].skill_set.all()
             logger.debug (" log 1 =>skill_list len %d is authenticated"%len(skill_list))
             tit_list = SkillTitle.objects.all() 
             year_list=[1,2,3,4,5,6,7,8,9,10,11,12]
             exp_level_list=[1,2,3,4,5]
             return render_to_response(
                      'skilladdcontact.html',
                       {'skill': skill_list,'ylist': year_list,'elist':exp_level_list,'title_list':tit_list,'user':request.user, 'contact_list':contacts_list,'skill_contact_list':skill_contact_list},
                       #{'form': form},
                       context_instance=RequestContext(request)
                     )#

def skilltitleaddform(request):
    #if (request.user.is_authenticated() == False):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    logger.debug("this is skill title add form")
    if request.method == 'POST':
        form = SkillTitleForm(request.POST)
        if form.is_valid():
            newdoc = SkillTitle(skill_title = request.POST['skill_title'])
            newdoc.save()
            return HttpResponseRedirect(reverse('modelsapp.views.skilltitleaddform'))
    else:
        form = SkillTitleForm()
    documents = SkillTitle.objects.all()
    return render_to_response(
        'skilltitleadd.html',
        {'skilltitle': documents, 'form': form,'user':request.user},
        #{'form': form},
        context_instance=RequestContext(request)
    )#
       

def deletecontactform(request,con_id):
    #if (request.user.is_authenticated() == False):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    logger.debug("this is edit contact form")
    contacts = Contact.objects.all()
    con_l = [] 
    for con in contacts:
        if int(con.supervisor.sup_id) == int(con_id):
           logger.debug( con.first_name)
           con_l.append(con)
    logger.debug("contacts len %s"%str(len(con_l)))
    if len(con_l) > 0:
        return render_to_response(
            'deletesupervisor.html',
            {'supcontacts': con_l},
            context_instance=RequestContext(request)
        )#
    else:
        del_contact = Contact.objects.get(id=con_id)
        logger.debug("deleting contact")
        logger.debug( con.first_name)
        del_contact.delete()
        logger.debug("deleted contact")
        return render_to_response(
            'contactdelete.html',
            {'contactid': con_id,'user':request.user},
            context_instance=RequestContext(request)
        )#
def editcontactform(request,con_id):
    #if (request.user.is_authenticated() == False):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    logger.debug("this is edit contact form")
    document = Contact.objects.get(id=con_id)
    # Handle file upload
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            picture1 = request.FILES['picture']
            c_id = request.POST['c_id']
            old_pic1 = request.POST['old_pic']
            last_name1 = request.POST['last_name']
            first_name1 = request.POST['first_name']
            sur_name1 = request.POST['sur_name']
            log_name1 = request.POST['log_name']
            email1 = request.POST['email']
            emp_id1 = request.POST['emp_id']
            phone1 = request.POST['phone']
            supervisor1 = request.POST['supervisor']
            jobtitle1 = request.POST['title']
            department1 = request.POST['department']
            H_No1 = request.POST['H_No']
            Line_1 = request.POST['Line1']
            street1 = request.POST['street']
            colony1 = request.POST['colony']
            city1 = request.POST['city']
            pin1 = request.POST['pin']
            add1 = Address(H_No=H_No1,Line1=Line_1,street=street1,colony=colony1,city=city1,pin=pin1)
            add1.save()
            pin1 = request.POST['pin']
            sup1 = Supervisor.objects.filter(sup_id=supervisor1)[0]
            job1 = JobTitle.objects.filter(title=jobtitle1)[0]
            dep1 = Department.objects.filter(dep_name=department1)[0]
            con_obj = Contact.objects.get(id=c_id)
            if sup1 and job1 and dep1:
               #newdoc = Contact(first_name=first_name1,last_name=last_name1,sur_name=sur_name1,email=email1,emp_id=emp_id1,supervisor=sup1,department=dep1,job_title=job1,phone=phone1,picture=picture1,address=add1)
               #newdoc.save()
               con_obj.first_name = first_name1
               con_obj.last_name = last_name1
               con_obj.sur_name = sur_name1
               con_obj.login_name = log_name1
               con_obj.email = email1
               con_obj.emp_id = emp_id1
               con_obj.supervisor = sup1
               con_obj.department = dep1
               con_obj.job_title = job1
               con_obj.phone = phone1
               con_obj.address = add1
               if picture == None:
                  con_obj.picture = old_pic1
               else:
                  con_obj.picture = picture1 
               con_obj.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('modelsapp.views.editcontact'))
    else:
        default_data={'c_id':document.id,'old_pic':document.picture,'picture':document.picture,'first_name':document.first_name,'last_name':document.last_name,'sur_name':document.sur_name,'log_name':document.login_name,'email':document.emp_id,'phone':document.phone,'email':document.email,'emp_id':document.emp_id,'H_No':document.address.H_No,'Line1':document.address.Line1,'street':document.address.street,'colony':document.address.colony,'city':document.address.city,'pin':document.address.pin}
        form = ContactForm(default_data) 

    # Load documents for the list page
    #documents = Document.objects.all()
    supervisors = Supervisor.objects.all()
    jobtitle = JobTitle.objects.all()
    department = Department.objects.all()
    users_list = User.objects.all()
    #users_list = []

    # Render list page with the documents and the form
    return render_to_response(
        'econtactform.html',
        #{'documents': documents, 'form': form},
        {'form': form,'supervisors':supervisors,'jobtitle':jobtitle,'department':department,'supervisor_id':document.supervisor.sup_id, 'jobtitle_name':document.job_title.title, 'department_name':document.department.dep_name,'picture':document.picture,'user':request.user,  'user_list':users_list},
        context_instance=RequestContext(request)
    )#

def viewcontact(request,con_id):
    #if (request.user.is_authenticated() == False):
    if request.user.is_authenticated():
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)

    document = Contact.objects.get(id=con_id)

    return render_to_response(
         'viewcontact2.html',
         {'document': document},
         #{'form': form},
         context_instance=RequestContext(request)
    )#

def supervisorform(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    # Handle file upload
    if request.method == 'POST':
        form = SupervisorForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Supervisor(sup_id = request.POST['sup_id'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('modelsapp.views.supervisorform'))
    else:
        form = SupervisorForm() # A empty, unbound form

    # Load documents for the list page
    documents = Supervisor.objects.all()
    contacts = Contact.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'supervisor.html',
        {'supervisor': documents, 'form': form, 'contacts':contacts,'user':request.user},
        #{'form': form},
        context_instance=RequestContext(request)
    )#

def deletesearchform(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    if request.method == 'POST':
        form = ESearchForm(request.POST, request.FILES)
        if form.is_valid():
            search_key = request.POST['search_key']
            documents0 = list(Contact.objects.filter(first_name__contains=search_key))
            documents1=list(Contact.objects.filter(last_name__contains=search_key))
            for doc in documents1:
                documents0.append(doc)
            documents2=list(Contact.objects.filter(sur_name__contains=search_key))
            for doc in documents2:
                documents0.append(doc)
            contact_id_list = []
            for doc in documents0:
               if contact_id_list.__contains__(doc.id):
                 pass
               else:
                  contact_id_list.append(doc.id)
            documents = []
            for con_id in contact_id_list:
                con_ob = Contact.objects.get(id=con_id)
                documents.append(con_ob)
            # Redirect to the document list after POST
            #return HttpResponseRedirect(reverse('modelsapp.views.esearchform'))
    else:
        form = ESearchForm() # A empty, unbound form
        documents = None

    # Load documents for the list page
    #documents = Department.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'dsearch.html',
        {'search': documents, 'form': form,'user':request.user},
        #{'form': form},
        context_instance=RequestContext(request)
    )#

def editsearchform(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    if request.method == 'POST':
        form = ESearchForm(request.POST, request.FILES)
        if form.is_valid():
            search_key = request.POST['search_key']
            documents0 = list(Contact.objects.filter(first_name__contains=search_key))
            documents1=list(Contact.objects.filter(last_name__contains=search_key))
            for doc in documents1:
                documents0.append(doc)
            documents2=list(Contact.objects.filter(sur_name__contains=search_key))
            for doc in documents2:
                documents0.append(doc)
            contact_id_list = []
            for doc in documents0:
               if contact_id_list.__contains__(doc.id):
                 pass
               else:
                  contact_id_list.append(doc.id)
            documents = []
            for con_id in contact_id_list:
                con_ob = Contact.objects.get(id=con_id)
                documents.append(con_ob)
            # Redirect to the document list after POST
            #return HttpResponseRedirect(reverse('modelsapp.views.esearchform'))
    else:
        form = ESearchForm() # A empty, unbound form
        documents = None

    # Load documents for the list page
    #documents = Department.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'esearch.html',
        {'search': documents, 'form': form, 'user':request.user},
        #{'form': form},
        context_instance=RequestContext(request)
    )#
def skillsearchform(request):
    if request.user.is_authenticated():
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    if request.method == 'POST':
        search_key = request.POST['title']
        co_list = Contact.objects.filter(skill__skill_name__contains=search_key)
    else:
        co_list = None
    tit_list = SkillTitle.objects.all() 
    logger.debug ("request user %d is authenticated"%len(tit_list))
    return render_to_response(
                 'skillsearch.html',
                  {'search': co_list,'title_list':tit_list, 'user':request.user},
                  context_instance=RequestContext(request)
    )#
     
def esearchform(request):
    if request.user.is_authenticated():
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    if request.method == 'POST':
        form = ESearchForm(request.POST, request.FILES)
        if form.is_valid():
            search_key = request.POST['search_key']
            documents0 = list(Contact.objects.filter(first_name__contains=search_key))
            documents1=list(Contact.objects.filter(last_name__contains=search_key))
            for doc in documents1:
                documents0.append(doc)
            documents2=list(Contact.objects.filter(sur_name__contains=search_key))
            for doc in documents2:
                documents0.append(doc)
            contact_id_list = []
            for doc in documents0:
               if contact_id_list.__contains__(doc.id):
                 pass
               else:
                  contact_id_list.append(doc.id)
            documents = []
            for con_id in contact_id_list:
                con_ob = Contact.objects.get(id=con_id)
                documents.append(con_ob)
            # Redirect to the document list after POST
            #return HttpResponseRedirect(reverse('modelsapp.views.esearchform'))
    else:
        form = ESearchForm() # A empty, unbound form
        documents = None

    # Load documents for the list page
    #documents = Department.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'search.html',
        {'search': documents, 'form': form},
        #{'form': form},
        context_instance=RequestContext(request)
    )#
def departmentform(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    # Handle file upload
    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Department(dep_name = request.POST['dep_name'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('modelsapp.views.departmentform'))
    else:
        form = DepartmentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Department.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'department.html',
        {'department': documents, 'form': form,'user':request.user},
        #{'form': form},
        context_instance=RequestContext(request)
    )#
def jobtitleform(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("request user %s is authenticated"%request.user.username)
    else:
        logger.debug ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    # Handle file upload
    if request.method == 'POST':
        form = JobTitleForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = JobTitle(title = request.POST['title'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('modelsapp.views.jobtitleform'))
    else:
        form = JobTitleForm() # A empty, unbound form

    # Load documents for the list page
    documents = JobTitle.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'jobtitle.html',
        {'jobtitle': documents, 'form': form,'user':request.user},
        #{'form': form},
        context_instance=RequestContext(request)
    )#

def login(request):
    c={}
    c.update(csrf(request))
    return render_to_response("login.html",c)
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/Contacts/login/")
    #auth_logout(request)


def adminindex(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password= password)
        if user.is_active:
            logger.error ( "error message use rname " + request.user.username)
            logger.debug ( "debug message use rname " + request.user.username)
            auth_login(request, user)
        else:
            logger.debug ( " rname " + request.user.username)
    return render_to_response(
            'adminindex.html',
            {'user':request.user},
            context_instance=RequestContext(request)
    )
    """
    if user.is_superuser:
        return render_to_response(
            'adminindex.html',
            {'user':request.user},
            context_instance=RequestContext(request)
        )
    else:
        return render_to_response(
            'userindex.html',
            {},
            context_instance=RequestContext(request)
        )
    """
def contactform(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        logger.debug ("debug request user %s is authenticated"%request.user.username)
        logger.error ("error request user %s is authenticated"%request.user.username)
    else:
        logger.error ("request user %s is authenticated"%request.user.username)
        c={}
        c.update(csrf(request))
        return render_to_response("login.html",c)
    # Handle file upload
    logger.debug ("contact form")
    if request.method == 'POST':
        logger.debug ("contact form1")
        logger.debug ("contact form1")
        form = ContactForm(request.POST, request.FILES)
        logger.debug (form.is_valid())
        if form.is_valid():
            logger.debug ("contact form2")
            picture1 = request.FILES['picture']
            c_id = request.POST['c_id']
            old_pic1 = request.POST['old_pic']
            last_name1 = request.POST['last_name']
            first_name1 = request.POST['first_name']
            sur_name1 = request.POST['sur_name']
            log_name1 = request.POST['log_name']
            logger.debug ("contact form2 %s"% (log_name1))
            email1 = request.POST['email']
            emp_id1 = request.POST['emp_id']
            phone1 = request.POST['phone']
            supervisor1 = request.POST['supervisor']
            jobtitle1 = request.POST['title']
            department1 = request.POST['department']
            H_No1 = request.POST['H_No']
            Line_1 = request.POST['Line1']
            street1 = request.POST['street']
            colony1 = request.POST['colony']
            city1 = request.POST['city']
            pin1 = request.POST['pin']
            add1 = Address(H_No=H_No1,Line1=Line_1,street=street1,colony=colony1,city=city1,pin=pin1)
            add1.save()
            pin1 = request.POST['pin']
            sup1 = Supervisor.objects.filter(sup_id=supervisor1)[0]
            job1 = JobTitle.objects.filter(title=jobtitle1)[0]
            dep1 = Department.objects.filter(dep_name=department1)[0]
            logger.debug (c_id)
            logger.debug ("old_pic1 " + str(old_pic1))
            if ((int(c_id) == 0) and (old_pic1 == '0')):
               logger.debug ("new contact saving")
               newdoc = Contact(first_name=first_name1,last_name=last_name1,sur_name=sur_name1,login_name=log_name1,email=email1,emp_id=emp_id1,supervisor=sup1,department=dep1,job_title=job1,phone=phone1,picture=picture1,address=add1)
               newdoc.save()
            elif ((int(c_id) > 0)):
               logger.debug ("edited contact saving")
               con_obj = Contact.objects.get(id=c_id)
               con_obj.first_name = first_name1
               con_obj.last_name = last_name1
               con_obj.sur_name = sur_name1
               con_obj.login_name = log_name1
               con_obj.email = email1
               con_obj.emp_id = emp_id1
               con_obj.supervisor = sup1
               con_obj.department = dep1
               con_obj.job_title = job1
               con_obj.phone = phone1
               con_obj.address = add1
               if picture1 == None:
                  con_obj.picture = old_pic1
               else:
                  con_obj.picture = picture1
               logger.debug("edit contact saving =>  %s"%log_name1)
               con_obj.save()
               logger.debug("edit contact saving =>  %s"%con_obj.login_name)


            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('modelsapp.views.contactform'))
    else:
        default_data={'c_id':0,'old_pic':'0'}
        form = ContactForm(default_data) # A empty, unbound form

    # Load documents for the list page
    #documents = Document.objects.all()
    supervisors = Supervisor.objects.all()
    jobtitle = JobTitle.objects.all()
    department = Department.objects.all()
    users_list = User.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'contactform.html',
        #{'documents': documents, 'form': form},
        {'form': form,'supervisors':supervisors,'jobtitle':jobtitle,'department':department,'user':request.user, 'user_list':users_list},
        context_instance=RequestContext(request)
    )#


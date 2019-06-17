import json
import urllib
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Hobby, Instructor, Customer, InstructorMessage, VisitInstructor, InstructorSearch, Follower
from hobby_event.models import HobbyEvent
from django.contrib import messages
from django.core.mail import send_mail
from smtplib import SMTPException
from django.contrib.auth.models import User
from allauth.account.views import SignupView
from .forms import InstructorForm, CustomerForm, InstructorSignUpForm, CustomerSignUpForm
from django.contrib.auth import logout as logout_function
import hobbyin.functions as functions

class InstructorSignUp(SignupView):
    template_name = 'custom_allauth/signup_instructor.html'
    form_class = InstructorSignUpForm
    redirect_field_name = 'next'
    view_name = 'instructor_sign_up'

    def get_context_data(self, **kwargs):
        ret = super(InstructorSignUp, self).get_context_data(**kwargs)
        ret.update(self.kwargs)
        return ret

class CustomerSignUp(SignupView):
    template_name = 'custom_allauth/signup_customer.html'
    form_class = CustomerSignUpForm
    redirect_field_name = 'next'
    view_name = 'customer_sign_up'

    def get_context_data(self, **kwargs):
        ret = super(CustomerSignUp, self).get_context_data(**kwargs)
        ret.update(self.kwargs)
        return ret

def compose_message(profile, message_text):
    subject =   "[Hobbyin] Du har fått en kundförfrågan!"
    message =   ["[KUNDINFORMATION]" + " \n\n",
                "Namn: " + profile.first_name + " " + profile.last_name + " \n",
                "Email: " + profile.email,
                "Telefonnummer: " + profile.telephone,
                " \n\n",
                "[MEDDELANDE]" + " \n\n" + message_text + " \n\n",
                "Med vänlig hälsning" + " \n\n",
                profile.first_name + " " + profile.last_name]

    message = "".join(message)
    return subject, message

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'There is still missing necessary information before you to get started.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Your account is inactive, contact maxhxie@gmail.com for help or more information.')
            return logout(request)

    hobbies = Hobby.objects.all()
    hobby_event_dictionary = {}
    if len(hobbies) == 0:
        hobbies = None

    else:
        hobby_event_dictionary = {}

        for hobby in hobbies:
            hobby_events = HobbyEvent.objects.filter(hobby=hobby, is_active=True, is_accepted=True, is_hidden=False)
            hobby_events = [event for event in hobby_events if event.has_happened == False]
            hobby_event_dictionary[hobby.hobby_name] = hobby_events

    return render(request, 'landing_page.html', context={'hobbies': hobbies, 'hobby_event_dictionary': hobby_event_dictionary})



def terms_of_use(request):
    return render(request, 'other_templates/terms_of_use.html')



def integrity(request):
    return render(request, 'other_templates/integrity.html')



def logout(request):
    logout_function(request)
    messages.info(request, 'Du har blivit utloggad')
    return index(request)



def settings(request):
    this_user = functions.get_this_user(request)
    if this_user != None:
        return render(request, 'settings_page.html', {'this_user': this_user})
    else:
        return index(request)



def profile_with_user(request, user_id):
    if request.user.is_authenticated:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'There is still missing necessary information before you to get started..')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Your account is inactive, contact maxhxie@gmail.com for help or more information.')
            return logout(request)

        this_user = functions.get_this_user(request)

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'This profile no longer exists.')
        return render(request, 'profile_page.html', context={'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    profile_model = functions.get_profile_model(user)
    try:
        profile = profile_model.objects.get(user=user)
    except profile_model.DoesNotExist:
        messages.error(request, 'This profile no longer exists.')
        return render(request, 'profile_page.html', context={'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})
    if profile.is_active == False:
        messages.error(request, 'This profile is inactive.')
        return render(request, 'profile_page.html', context={'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    return render(request, 'profile_page.html', context={'profile':profile, 'this_user': this_user, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})


def send_instructor_message(request, user_id, hobby):
    try:
        instructor_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'This profile is inactive.')
        return profile_with_user_hobby(request, user_id, hobby)

    if request.user.is_authenticated:
        if request.method == "POST":
            message_text = request.POST.get('message_text')
            if len(message_text) > 2500:
                messages.error(request, 'Your message cannot exceed 2500 symbols.')
                return profile_with_user_hobby(request, user_id, hobby)
            profile_model = functions.get_profile_model(request.user)
            if profile_model != None:
                profile = profile_model.objects.get(user=request.user)
                if instructor_user == profile.user:
                    messages.error(request, 'You cannot send messages to yourself.')
                    return profile_with_user_hobby(request, user_id, hobby)
                message_object = InstructorMessage.objects.create(to_user=instructor_user, first_name=profile.first_name, last_name=profile.last_name, email=profile.email, telephone=profile.telephone, message=message_text)
                mail_subject, mail_message = compose_message(profile, message_text)
                try:
                    send_mail(mail_subject, mail_message, 'hobbyin.se@gmail.com', [instructor_user.email])
                    message_objects.message_sent = True
                    message_objects.save()
                except SMTPException:
                    messages.error(request, 'Your message could not be sent.')
                    return profile_with_user_hobby(request, user_id, hobby)
                messages.success(request, 'Ditt meddelande har blivit skickat.')
                return profile_with_user_hobby(request, user_id, hobby)
            else:
                messages.error(request, 'Something went wrong, contact us and we will help you.')
                return logout(request)
        else:
            messages.error(request, "Your message could not be sent.")
            return profile_with_user_hobby(request, user_id, hobby)
    else:
        messages.error(request, "You have to be logged in to send messages.")
        return profile_with_user_hobby(request, user_id_hobby)



def my_profile(request):
    ## User is redirected here upon LOGIN
    this_user = functions.get_this_user(request)
    if this_user != None:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'There is still missing necessary information before you to get started.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Your account is inactive, contact maxhxie@gmail.com for help or more information.')
            return logout(request)
        else:
            if functions.is_instructor(request) or functions.is_customer(request):
                return profile_with_user(request, this_user.id)
            else:
                messages.error(request, 'Something went really wrong, contact maxhxie@gmail.com and we will help you.')
                return logout(request)
    else:
        messages.error(request, 'You are not logged in.')
        return redirect('account_login')



def edit_profile(request):
    this_user = functions.get_this_user(request)
    if this_user != None:

        if functions.is_instructor(request):
            account_form = InstructorForm
            account_obj = this_user.instructor
        elif functions.is_customer(request):
            account_form = CustomerForm
            account_obj = this_user.customer
        else:
            messages.error(request, 'Something went really wrong, contact maxhxie@gmail.com and we will help you.')
            return index(request)

        if request.method == "POST":
            form = account_form(request.POST, request.FILES, instance=account_obj)
            if form.is_valid():
               form.save()
               account_obj.valid_profile = True
               account_obj.save()
               messages.success(request, 'Your profile has been changed.')
               request.method = "GET"
               return my_profile(request)
            else:
                messages.error(request, 'You profile was not changed. Double check to see that yourinformation is correct.')
                return render(request, 'edit_profile_page.html', context={'form': form})
        else:
            form = account_form(None, instance=account_obj)
            return render(request, 'edit_profile_page.html', context={'form': form})

    else:
        messages.error(request, 'You are not logged in.')
        return redirect('account_login')



def follow_instructor(request):
    if request.user.is_authenticated:
        this_user = functions.get_this_user(request)
        profile_model = functions.get_profile_model(this_user)
        if request.method == "POST":
            user_id = request.POST.get('user_id')
        else:
            return my_profile(request)

        try:
            instructor_user = User.objects.get(pk=user_id)
            temp_model = functions.get_profile_model(instructor_user)
            if temp_model != Instructor:
                messages.error(request, 'You can only follow instructors.')
                return profile_with_user(request, user_id)
        except User.DoesNotExist:
            messages.error(request, 'This profile no longer exists.')
            return profile_with_user(request, user_id)

        try:
            Follower.objects.get(instructor=instructor_user.instructor, follower=this_user)
            messages.error(request, 'You are already following ' + instructor_user.instructor.first_name + ' ' + instructor_user.instructor.last_name + '.')
            return profile_with_user(request, user_id)
        except Follower.DoesNotExist:
            pass

        if profile_model == None:
            messages.error(request, 'You are not authorized to follow this profile')
            return profile_with_user(request, user_id)
        else:
            profile_model.objects.get(user=this_user)
            if this_user == instructor_user:
                messages.error(request, 'You cannot follow yourself')
                return profile_with_user(request, user_id)
            else:
                Follower.objects.create(instructor=instructor_user.instructor, follower=this_user)
                messages.success(request, 'You are now following ' + instructor_user.instructor.first_name + ' ' + instructor_user.instructor.last_name)
                return profile_with_user(request, user_id)

    else:
        messages.error(request, 'You have to be logged in')
        return profile_with_user(request, user_id)

def unfollow_instructor(request):
    if request.user.is_authenticated:
        this_user = functions.get_this_user(request)
        profile_model = functions.get_profile_model(this_user)
        if request.method == "POST":
            user_id = request.POST.get('user_id')
        else:
            return my_profile(request)

        try:
            instructor_user = User.objects.get(pk=user_id)
            temp_model = functions.get_profile_model(instructor_user)
            if temp_model != Instructor:
                messages.error(request, 'You can only unfollow users.')
                return profile_with_user(request, user_id)
        except User.DoesNotExist:
            messages.error(request, 'This profile no longer exists.')
            return profile_with_user(request, user_id)

        if profile_model == None:
            messages.error(request, 'You are not authorized to unfollow instructors.')
            return profile_with_user(request, user_id)
        else:
            profile_model.objects.get(user=this_user)
            if this_user == instructor_user:
                messages.error(request, 'You cannot unfollow yourself.')
                return profile_with_user(request, user_id)
            else:
                follow_objects = Follower.objects.filter(instructor=instructor_user.instructor, follower=this_user)
                if len(follow_objects) == 0:
                    messages.error(request, 'You are already not following this user.')
                    return profile_with_user(request, user_id)
                else:
                    for object in follow_objects:
                        object.delete()
                messages.info(request, 'You have unfollowed ' + instructor_user.instructor.first_name + ' ' + instructor_user.instructor.last_name)
                return profile_with_user(request, user_id)

    else:
        messages.error(request, 'You have to be logged in.')
        return profile_with_user(request, user_id)

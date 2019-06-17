from external_page.models import Instructor, Customer, Hobby, InstructorMessage
from django.forms import ModelForm
from django.db import models
from django.utils.safestring import mark_safe
from django import forms
from allauth.account.forms import SignupForm
from django.forms import TextInput, Select, Textarea, RadioSelect, CheckboxInput, NumberInput, CheckboxSelectMultiple
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext as _
import hobbyin.functions as functions
import re

class CheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, *args, **kwargs):
        output = super(CheckboxSelectMultiple, self).render(*args, **kwargs)
        output = output.replace(u'<li>', u'')
        output = output.replace(u'</li>', u'')
        return mark_safe(output.replace(u'<ul id="id_hobbies">', u''))

class InstructorSignUpForm(SignupForm):
    def save(self, request):
        user = super(InstructorSignUpForm, self).save(request)
        user.save()
        functions.create_instructor(user)
        return user

class CustomerSignUpForm(SignupForm):
    def save(self, request):
        user = super(CustomerSignUpForm, self).save(request)
        user.save()
        functions.create_customer(user, email=user.email)
        return user

class InstructorForm(ModelForm):
    honeypot = forms.CharField(required=False,widget=forms.HiddenInput)
    class Meta:
        model = Instructor
        fields = ['profile_picture', 'first_name', 'last_name', 'city', 'city_district', 'zip_code', 'description']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname'}),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'City... e.g. Stockholm, London...'}),
            'city_district': TextInput(attrs={'class': 'form-control', 'placeholder': 'Municipality: e.g. Sollentuna, Täby...'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip code: e.g. 191 41...'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Short biography about yourself: Hey...', 'rows':20}),
        }
        error_messages = {
            'first_name': {
                'required': _('Du måste fylla i ditt förnamn'),
                'max_length': _('The inputted text was too long.'),
            },
            'last_name': {
                'required': _('Du måste fylla i ditt efternamn'),
                'max_length': _('The inputted text was too long.'),
            },
            'city': {
                'required': _('Du måste fylla i din stad'),
                'max_length': _('The inputted text was too long.'),
            },
            'city_district': {
                'required': _('Du måste fylla i din kommun/stadsdel'),
                'max_length': _('The inputted text was too long.'),
            },
            'zip_code': {
                'required': _('Du måste fylla i ditt postnummer'),
                'max_length': _('The inputted text was too long.'),
            },
            'description': {
                'max_length': _('The inputted text was too long, max 2500 symbols'),
            },
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', first_name):
            raise forms.ValidationError(("You have used invalid symbols in this field"), code="invalid_first_name")
        else:
            return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', last_name):
            raise forms.ValidationError(("You have user invalid symbols in this field"), code="invalid_last_name")
        else:
            return last_name

    def clean_city(self):
        city = self.cleaned_data['city']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', city):
            raise forms.ValidationError(("You have user invalid symbols in this field"), code="invalid_city")
        else:
            return city

    def clean_city_district(self):
        city_district = self.cleaned_data['city_district']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', city_district):
            raise forms.ValidationError(("You have user invalid symbols in this field"), code="invalid_city_district")
        else:
            return city_district

    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code']
        if not re.match(r'^(\d{5}|\d{3}[\s]\d{2}|\d{3}-\d{2})$', zip_code):
            raise forms.ValidationError(_("Du must enter a valid zip coder"), code="invalid_zip_code")
        else:
            return zip_code

    def clean_profile_picture(self):
        try:
            profile_picture = self.cleaned_data['profile_picture']

            try:
                w, h = get_image_dimensions(profile_picture)

                #validate dimensions
                max_width = 1080
                max_height = 1080
                if w > max_width or h > max_height:
                    raise forms.ValidationError(_('Your profile picture cannot exceed %s pixles in width and not %s pixles in height') % (max_width, max_height))

                #validate content type
                main, sub = profile_picture.content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'jpg', 'png']):
                    raise forms.ValidationError(_('You have to upload a .jpg or a .png file.'))

                #validate file size
                if len(profile_picture) > (1000 * 1024):
                    raise forms.ValidationError(_('Your profile picture may not exceed 1Mb in size'))

            except AttributeError:
                """
                Handles case when we are updating the user profile
                and do not supply a new profile_picture
                """
                pass

            return profile_picture

        except:
            pass

    def clean_honeypot(self):
        honeypot = self.cleaned_data['honeypot']
        if len(honeypot):
            raise forms.ValidationError()
        else:
            return honeypot

    def clean(self):
        cleaned_data=super(InstructorForm, self).clean()


class CustomerForm(ModelForm):
    honeypot = forms.CharField(required=False,widget=forms.HiddenInput)
    class Meta:
        model = Customer
        fields = ['profile_picture', 'first_name', 'last_name', 'telephone', 'zip_code']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Efternamn'}),
            'telephone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefonnummer'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Postnummer: ex. 123 45...'}),
        }
        error_messages = {
            'first_name': {
                'required': _('You have to fill in your first name'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'last_name': {
                'required': _('You have to fill in your surname'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'telephone': {
                'required': _('You have to fill in your telephone number'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'zip_code': {
                'required': _('You have to fill in your zip code'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', first_name):
            raise forms.ValidationError(_("You have used invalid symbols in this field"), code="invalid_first_name")
        else:
            return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', last_name):
            raise forms.ValidationError(_("You have used invalid symbols in this field"), code="invalid_last_name")
        else:
            return last_name

    def clean_telephone(self):
        telephone = self.cleaned_data['telephone']
        mobile_regex = r'^(\+46|0|\(\+46\)) *(7[0236])( |-|)(\d{4} \d{3}|\d{3} \d{4}|\d{3} \d{2} \d{2}|\d{2} \d{2} \d{3}|\d{7})$'
        home_phone_regex = r'^(\+46|0|\(\+46\)) *(8)( |-|)(\d{4} \d{2}|\d{2} \d{4}|\d{3} \d{3}|\d{2} \d{2} \d{2}|\d{6})$'
        if re.match(mobile_regex, telephone) or re.match(home_phone_regex, telephone):
            return telephone
        else:
            raise forms.ValidationError(_("You have to enter a valid telephone number"), code="invalid_telephone")

    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code']
        if not re.match(r'^(\d{5}|\d{3}[\s]\d{2}|\d{3}-\d{2})$', zip_code):
            raise forms.ValidationError(_("You have to enter a valid zip code"), code="invalid_zip_code")
        else:
            return zip_code

    def clean_profile_picture(self):
        try:
            profile_picture = self.cleaned_data['profile_picture']

            try:
                w, h = get_image_dimensions(profile_picture)

                #validate dimensions
                max_width = 1080
                max_height = 1080
                if w > max_width or h > max_height:
                    raise forms.ValidationError(_('Your profile picture must not be larger than %s pixles on width or %s on height') % (max_width, max_height))

                #validate content type
                main, sub = profile_picture.content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'jpg', 'png']):
                    raise forms.ValidationError(_('You have to upload a .jpg or a .png file'))

                #validate file size
                if len(profile_picture) > (1000 * 1024):
                    raise forms.ValidationError(_('Your profile picture may not exceed 1Mb in size'))

            except AttributeError:
                """
                Handles case when we are updating the user profile
                and do not supply a new profile_picture
                """
                pass

            return profile_picture

        except:
            pass

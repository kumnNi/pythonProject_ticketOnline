from datetime import date, datetime

from django import forms
from django.utils import timezone

from veranstaltung.models import Event, EventLocation, Category, User, UserProfile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class DateInput(forms.DateInput):
    input_type = 'date'


class UpdateEventForm(forms.ModelForm):

    class Meta:
        model = Event  # Specify the model to be updated
        fields = ['name', 'datum', 'ticketAvailability', 'price', 'artist', 'locationID', 'categoryID', 'userID',
                  'video_source', 'img_source']

        widgets = {
            'datum': DateInput(),
            'userID': forms.HiddenInput(),
        }

class UpdateEventLocationForm(forms.ModelForm):
    class Meta:
        model = EventLocation  
        fields = ['location', 'standort', 'seatingCapacity', 'detail', 'userID']

        widgets = {
            'userID': forms.HiddenInput(),
        }

    def clean_location(self):
        location = self.cleaned_data['location']
        if len(location) < 3:
            raise forms.ValidationError('Die Location ist zu kurz: Muss mindestens 3 Zeichen enthalten')
        return location

    def clean_standort(self):
        standort = self.cleaned_data['standort']
        if len(standort) < 3:
            raise forms.ValidationError('Die standort ist zu kurz: Muss Address eingeben')
        return standort


    def clean_detail(self):
        standort = self.cleaned_data['detail']
        if len(standort) < 3:
            raise forms.ValidationError('Die standort ist zu kurz: Muss mindesten 3 Zeichen')
        return standort


class UpdateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description']
        #widgets = {'eventID': forms.Select(attrs={'class': 'form-control'})}

    # eventID = forms.ModelChoiceField(
    #     queryset=Event.objects.all(),
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    #     # to_field_name='title',
    #     label='event'
    #)

#https://www.linkedin.com/pulse/enable-login-register-email-django-oleksandr-honcharenko
class CustomUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user', 'nickname', 'birthday']

        widgets = {
            'birthday': DateInput(),
        }


CustomUserCreateFormSet = forms.inlineformset_factory(User,UserProfile, form=UserProfileForm, fields=['nickname','birthday'], can_delete=False)


class CombinedForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []






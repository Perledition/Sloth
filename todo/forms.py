
from django.forms import NumberInput
from .models import Project, UserProfile, FirstFeed
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.files.images import get_image_dimensions


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields=['pro_title', 'pro_desc', 'pro_pic']


class TodoForm(forms.Form):

    task_title = forms.CharField(max_length=50,
                                 widget=forms.TextInput(
                                     attrs={'size': 40}))

    task_explain = forms.CharField(max_length=5000,
                                   widget=forms.Textarea(
                                       attrs={'col':25, 'row':50, 'size': 5}))

    task_imp = forms.IntegerField(widget= NumberInput(attrs={'type':'range', 'step': '1', 'max':10, 'min': 0,
                                                             'class':'slider', 'size': 40}))

    task_eff_hour = forms.ChoiceField(choices=[(x,x)for x in range(0,150)])
    task_eff_minutes = forms.ChoiceField(choices=[(x,x)for x in range(0, 60, 5)])

    project = forms.CharField(max_length=40)

    hour = forms.ChoiceField(choices=[(x, x) for x in range(0, 25)])

    minutes = forms.ChoiceField(choices=[(x, x) for x in range(00, 60, 5)])


class ItemForm(forms.Form):
    Item_title=forms.CharField(max_length=30)


class UserForm(UserChangeForm):

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
        ]


class UserLoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields=[
            'email',
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class UserAgree(forms.Form):
    agree = forms.BooleanField(initial=False)


class FirstFeedForm(forms.Form):
    class Meta:
        model = FirstFeed
        fields = [
            'post_time',
            'how',
            'impress',
            'impact',
            'opinion',
            'mail'
        ]

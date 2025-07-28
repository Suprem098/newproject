from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, StudyMaterial, Feedback

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email Address")
    username = forms.CharField(required=True, label="Username")

    class Meta:
        model = Profile
        fields = ['role']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            profile.save()
        return profile

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'description', 'department', 'semester', 'subject', 'file']

class StudyMaterialFilterForm(forms.Form):
    search = forms.CharField(required=False, label='Search')
    subject = forms.CharField(required=False, label='Subject')
    semester = forms.ChoiceField(required=False, choices=[('', 'All Semesters')] + [(str(i), str(i)) for i in range(1, 9)], label='Semester')
    faculty = forms.ChoiceField(required=False, choices=[], label='Faculty')
    date_uploaded_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Date From')
    date_uploaded_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Date To')

    def __init__(self, *args, **kwargs):
        faculty_choices = kwargs.pop('faculty_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['faculty'].choices = [('', 'All Departments')] + [(val, label) for val, label in faculty_choices]

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comments']

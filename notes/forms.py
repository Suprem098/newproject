from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, StudyMaterial, Feedback

class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].required = True  # Ensure it's bound

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        role = self.cleaned_data.get('role')  # Don't default to student here
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
        return user

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = [
            'title',
            'description',
            'file',
            'department',
            'semester',
            'subject',
            'chapter_name',
        ]

class StudyMaterialFilterForm(forms.Form):
    subject = forms.CharField(max_length=200, required=False)
    semester = forms.ChoiceField(
        choices=[('', 'All')] + StudyMaterial.SEMESTER_CHOICES,
        required=False
    )
    faculty = forms.CharField(max_length=150, required=False)
    date_uploaded_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_uploaded_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    search = forms.CharField(max_length=200, required=False)

class FeedbackForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        label="Rating (1-5)"
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Comments"
    )

    class Meta:
        model = Feedback
        fields = ['rating', 'comments']

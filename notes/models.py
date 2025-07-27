from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class StudyMaterial(models.Model):
    SEMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
        ('3', '3rd Semester'),
        ('4', '4th Semester'),
        ('5', '5th Semester'),
        ('6', '6th Semester'),
        ('7', '7th Semester'),
        ('8', '8th Semester'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='study_materials/')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    subject = models.CharField(max_length=200)
    chapter_name = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True, help_text="Extracted text content from PDF for search")

    def __str__(self):
        return self.title

class Feedback(models.Model):
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.study_material.title}"

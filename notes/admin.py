from django.contrib import admin
from .models import Profile, Department, StudyMaterial

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'uploaded_by', 'upload_date')
    list_filter = ('department', 'upload_date')
    search_fields = ('title', 'description')

from django.contrib import admin
from .models import Notice

admin.site.register(Notice)
from .models import Profile, Department, StudyMaterial, Feedback

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

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('study_material', 'user', 'rating', 'created_at')

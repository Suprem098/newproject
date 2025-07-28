from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.db.models import Q
import logging

from .forms import UserRegisterForm, StudyMaterialForm, StudyMaterialFilterForm, FeedbackForm, ProfileForm
from .models import StudyMaterial, Department, Feedback, Profile

logger = logging.getLogger(__name__)

from .models import Notice

def home(request):
    notices = Notice.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'notes/home.html', {'notices': notices})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure profile exists
            from .models import Profile
            from django.db.utils import IntegrityError
            try:
                Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                Profile.objects.create(user=user, role='student')
            login(request, user)
            return redirect('notes:home')
    else:
        form = UserRegisterForm()
    return render(request, 'notes/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('notes:home')
    else:
        form = AuthenticationForm()
    return render(request, 'notes/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('notes:home')

@login_required
def upload_study_material(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Create profile with default role if missing
        profile = Profile.objects.create(user=request.user, role='student')
        logger.info(f"Created missing profile for user {request.user.username} with default role 'student'.")
    role_raw = profile.role
    logger.info(f"User {request.user.username} profile role raw value: {repr(role_raw)} (type: {type(role_raw)})")
    role = role_raw.lower().strip() if role_raw else ''
    logger.info(f"User {request.user.username} with normalized role {repr(role)} attempting upload.")

    if not (request.user.is_staff or role == 'teacher'):
        logger.warning(f"User {request.user.username} denied upload. Role: {repr(role_raw)}")
        return HttpResponseForbidden("Only teachers or admins can upload materials.")

    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            study_material = form.save(commit=False)
            study_material.uploaded_by = request.user
            study_material.save()
            return redirect('notes:study_material_list')
        else:
            logger.warning(f"Form errors: {form.errors}")
    else:
        form = StudyMaterialForm()
    
    return render(request, 'notes/upload.html', {'form': form})

@login_required
def study_material_list(request):
    departments = Department.objects.all()
    faculty_choices = [(dept.name, dept.name) for dept in departments]

    # Get unique subjects for filter dropdown
    subjects = StudyMaterial.objects.values_list('subject', flat=True).distinct().order_by('subject')

    filter_form = StudyMaterialFilterForm(request.GET, faculty_choices=faculty_choices)
    study_materials = StudyMaterial.objects.all()

    if filter_form.is_valid():
        subject = filter_form.cleaned_data.get('subject')
        semester = filter_form.cleaned_data.get('semester')
        faculty = filter_form.cleaned_data.get('faculty')
        date_from = filter_form.cleaned_data.get('date_uploaded_from')
        date_to = filter_form.cleaned_data.get('date_uploaded_to')
        search = filter_form.cleaned_data.get('search')

        if subject:
            study_materials = study_materials.filter(department__name__icontains=subject)
        if semester:
            study_materials = study_materials.filter(semester__icontains=semester)
        if faculty:
            study_materials = study_materials.filter(department__name__icontains=faculty)
        if date_from:
            study_materials = study_materials.filter(upload_date__gte=date_from)
        if date_to:
            study_materials = study_materials.filter(upload_date__lte=date_to)
        if search:
            study_materials = study_materials.filter(
                Q(title__icontains=search) |
                Q(department__name__icontains=search) |
                Q(subject__icontains=search) |
                Q(extracted_text__icontains=search)
            )

    return render(request, 'notes/study_material_list.html', {
        'study_materials': study_materials,
        'departments': departments,
        'filter_form': filter_form,
        'subjects': subjects,
    })

@login_required
def download_study_material(request, pk):
    study_material = get_object_or_404(StudyMaterial, pk=pk)
    file_handle = study_material.file.open()
    response = HttpResponse(file_handle.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{study_material.file.name.split("/")[-1]}"'
    study_material.file.close()
    return response

@login_required
def autocomplete_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []
    if query:
        materials = StudyMaterial.objects.filter(
            Q(title__icontains=query) | Q(subject__icontains=query)
        ).values_list('title', flat=True).distinct()[:10]
        suggestions = list(materials)
    return JsonResponse({'results': suggestions})

@login_required
def submit_feedback(request, study_material_id):
    study_material = get_object_or_404(StudyMaterial, pk=study_material_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.study_material = study_material
            feedback.user = request.user
            feedback.save()
            return redirect('notes:study_material_list')
    else:
        form = FeedbackForm()
    return render(request, 'notes/submit_feedback.html', {'form': form, 'study_material': study_material})

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'notes/profile.html', {'profile': profile})

@login_required
def profile_edit(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('notes:profile_view')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'notes/profile_edit.html', {'form': form})

from typing import Any, Dict
from django.http import HttpRequest, HttpResponse

@login_required
def notifications_list(request: HttpRequest) -> HttpResponse:
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    context: Dict[str, Any] = {'notifications': notifications}
    return render(request, 'notes/notifications_list.html', context)

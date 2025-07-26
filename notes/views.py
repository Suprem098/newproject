from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from .forms import UserRegisterForm, StudyMaterialForm, StudyMaterialFilterForm, FeedbackForm
from .models import StudyMaterial, Department, Feedback
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden

def home(request):
    return render(request, 'notes/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
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
    # Allow only teachers and admin (staff) to upload
    if not (request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'teacher')):
        return HttpResponseForbidden("You do not have permission to upload study materials.")

    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            study_material = form.save(commit=False)
            study_material.uploaded_by = request.user
            # TODO: Extract text from PDF and save to extracted_text field
            study_material.save()
            return redirect('notes:study_material_list')
    else:
        form = StudyMaterialForm()
    return render(request, 'notes/upload.html', {'form': form})

@login_required
def study_material_list(request):
    filter_form = StudyMaterialFilterForm(request.GET)
    study_materials = StudyMaterial.objects.all()
    departments = Department.objects.all()
    subjects = StudyMaterial.objects.values_list('department__name', flat=True).distinct()

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
            study_materials = study_materials.filter(uploaded_by__username__icontains=faculty)
        if date_from:
            study_materials = study_materials.filter(upload_date__gte=date_from)
        if date_to:
            study_materials = study_materials.filter(upload_date__lte=date_to)
        if search:
            study_materials = study_materials.filter(
                Q(title__icontains=search) |
                Q(department__name__icontains=search) |
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

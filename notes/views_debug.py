from django.http import JsonResponse
from django.contrib.auth.models import User

def list_users_profiles(request):
    users = User.objects.all()
    data = []
    for user in users:
        profile = getattr(user, 'profile', None)
        role = profile.role if profile else None
        data.append({
            'username': user.username,
            'email': user.email,
            'profile_role': role,
        })
    return JsonResponse(data, safe=False)

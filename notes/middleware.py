from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import Profile

class RefreshUserProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user and not isinstance(user, AnonymousUser):
            try:
                # Refresh the profile from the database
                user.profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                user.profile = None

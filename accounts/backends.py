from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User = get_user_model()

class ApprovedUserBackend(ModelBackend):
    def user_can_authenticate(self, user):
        if not user.is_active:
            return False

        if hasattr(user, "is_approved") and not user.is_approved:
            raise PermissionDenied("Account pending approval")

        return True

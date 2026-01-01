from django.core.exceptions import PermissionDenied

def role_required(*roles):
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

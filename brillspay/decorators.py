from django.shortcuts import redirect
from django.contrib import messages

def parent_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'PARENT':
            messages.error(request, "Access denied.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'STAFF':
            messages.error(request, "Access denied.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

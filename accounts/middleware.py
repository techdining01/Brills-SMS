import time
from django.contrib.auth import logout
from django.shortcuts import redirect


class IdleTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = time.time()
            last_activity = request.session.get('last_activity')

            if last_activity:
                if now - last_activity > 1200:  # 20 minutes
                    logout(request)
                    request.session.flush()
                    return redirect('accounts:login')

            request.session['last_activity'] = now

        response = self.get_response(request)
        return response


from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            excluded = [
                reverse("accounts:complete_profile"),
                reverse("accounts:logout"),
            ]

            if (
                not request.user.address
                and request.path not in excluded
            ):
                return redirect("accounts:complete_profile")

        return self.get_response(request)

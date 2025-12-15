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
                    return redirect('login')

            request.session['last_activity'] = now

        response = self.get_response(request)
        return response

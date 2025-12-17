from django.contrib import admin
from django.shortcuts import render, redirect


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')
    return render(request, 'exams/landing_page.html')



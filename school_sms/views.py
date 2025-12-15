from django.contrib import admin
from django.shortcuts import render, redirect


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('post_login_router')
    return render(request, 'exams/landing_page.html')


# from django.http import HttpResponse

# # def landing_page(request):
# #     return HttpResponse("LANDING PAGE — NO AUTH — OK")

# def landing_page(request):
#     return render(request, 'core/landing_raw.html')
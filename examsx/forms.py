from django import forms
from .models import Exam, SchoolClass, Subject


class ClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'level', 'description', 'academic_year', 'teacher', 'assistant_teacher', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class Name'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A, B, C or Science, Arts'}),
            'teacher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teacher name'}),
            'assistant_teacher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assistant Teacher'}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'department', 'classes', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject Name'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'classes': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "title",
            "school_class",
            "duration",
            "start_time",
            "end_time",
            "is_active",
            "is_published",
            "allow_retake",
            "requires_payment",
            "price",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Exam Title"}),
            "school_class": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter School Class"}),
            "duration": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Duration"}),
            "start_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "allow_retake": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "requires_payment": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Price"}),

        }

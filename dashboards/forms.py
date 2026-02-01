from django import forms
from django.contrib.auth import get_user_model
from exams.models import SchoolClass, Exam

User = get_user_model()

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'level', 'academic_year', 'description', 'teacher', 'assistant_teacher', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. JSS 1A'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2023/2024'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'assistant_teacher': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter teachers for teacher and assistant_teacher fields
        self.fields['teacher'].queryset = User.objects.filter(role=User.Role.TEACHER)
        self.fields['assistant_teacher'].queryset = User.objects.filter(role=User.Role.TEACHER)


class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False, help_text="Leave empty to keep existing password (for edits) or auto-generate (for new).")
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'student_class', 'admission_number', 'phone_number', 'address', 'password', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. adigun_123'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 08012345678'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. jdoe123'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not user.pk:  # New user and no password provided
             # Set a default password or handle as needed. For now, default 'password123'
             user.set_password('password123') 
        if commit:
            user.save()
        return user

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'school_class', 'duration', 'start_time', 'end_time', 'passing_marks', 'is_active', 'is_published', 'allow_retake']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. First Term Exam Math'}),
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_retake': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

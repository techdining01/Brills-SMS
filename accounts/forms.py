from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Student, Teacher, Parent



class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username or Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'id': 'password'
    }))



class BaseUserCreateForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')


    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned


class StudentCreateForm(BaseUserCreateForm):
    class Meta(BaseUserCreateForm.Meta):
        model = Student
        fields = BaseUserCreateForm.Meta.fields + ('student_class',)


class TeacherCreateForm(BaseUserCreateForm):
    class Meta(BaseUserCreateForm.Meta):
        model = Teacher
        fields = BaseUserCreateForm.Meta.fields


class ParentCreateForm(BaseUserCreateForm):
    class Meta(BaseUserCreateForm.Meta):
        model = Parent
        fields = BaseUserCreateForm.Meta.fields


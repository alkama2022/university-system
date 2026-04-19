from django.forms import ModelForm
from .models import Course,Registration,Student
from django import forms
from .models import Student

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'


class StudentForm(ModelForm):
    class Meta:
       model = Student
       fields = '__all__'
      
    
class EnrollmentForm(ModelForm):
    class Meta:
        model = Registration
        fields = ['student','course']
        
class LoginForm(ModelForm):
        model = Student
        fields = ['registration_number','email','department','level']
# # forms.py

# class RegisterForm(ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']


# class StudentProfileForm(ModelForm):
#     class Meta:
#         model = Student
#         fields = ['department', 'level']

from django.forms import ModelForm
from .models import Course,Registration,Student,Complaint
from django import forms
from .models import Student
from django import forms
from .models import Complaint, Course

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['course', 'complaint_type', 'subject', 'session', 'description', 'priority']

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)  # receive student
        super().__init__(*args, **kwargs)

        if student:
            self.fields['course'].queryset = Course.objects.filter(
                depertiment=student.department,
                level=student.level,
                # session=student.session
            )
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


from django.forms import ModelForm
from .models import Course,Registration,Complaint
from django import forms


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


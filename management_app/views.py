from django.shortcuts import render
from .models import Timetable
# Create your views here.

def show_tible(request):
    student = request.user.student
    first_semester_queryset = Timetable.objects.filter(semester__semester_type = 'FIRST')
    second_semester_queryset = Timetable.objects.filter(semester__semester_type = 'SECOND')
    context = {
    "student": student,
    "first_semester_timetable": first_semester_queryset,
    "second_semester_timetable": second_semester_queryset,
    }

    return render(request,'management_apps/timetable.html',context)
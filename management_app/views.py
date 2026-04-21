from django.shortcuts import render
from .models import Timetable
from collections import defaultdict
# Create your views here.
#===========================================================
#              HELPER FUNCTION TO SHOW TIMETABLE
#===========================================================
def show_timetable(timetable_queryset):
    grouped_timetable = defaultdict(list)
    for t in timetable_queryset:
        key = t.day
        grouped_timetable[key].append(t)
    return grouped_timetable

#===========================================================
#              VIEW FUNCTION TO DISPLAY TIMETABLE
#===========================================================

def show_timetable_view(request):
    student = request.user.student
    first_semester_queryset = show_timetable(Timetable.objects.filter(semester__semester_type = 'FIRST'))
    second_semester_queryset = show_timetable(Timetable.objects.filter(semester__semester_type = 'SECOND'))
    context = {
    "student": student,
    "first_semester_timetable": first_semester_queryset,
    "second_semester_timetable": second_semester_queryset,
    }

    return render(request,'management_apps/timetable.html',context)
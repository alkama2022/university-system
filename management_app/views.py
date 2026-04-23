from django.shortcuts import render
from django.http import HttpResponse
from .models import Timetable,Result
from collections import defaultdict
from pprint import pprint

# Create your views here.
#===========================================================
#              HELPER FUNCTION TO SHOW TIMETABLE
#===========================================================
def show_timetable(timetable_queryset):
    grouped_timetable = defaultdict(list)
    for t in timetable_queryset:
        grouped_timetable[t.day].append(t) # key = t.day value = list of timetable entries for that day
    return grouped_timetable

def calculate_gpa(result_queryset):
    total_gpa:float = 0
    gpa_length = 0
    for result in result_queryset:
        if result.grade_point != 0:
            total_gpa += result.grade_point
            gpa_length += 1
    return total_gpa/gpa_length
#===========================================================
#              VIEW FUNCTION TO DISPLAY TIMETABLE
#===========================================================

def show_timetable_view(request):
    student = request.user.student
   
    base_queryset = Timetable.objects.filter(
        department=student.department,
        level=student.level
    ).select_related('course', 'lecturer', 'venue', 'semester')

    first_semester = show_timetable(
        base_queryset.filter(semester__semester_type='FIRST')
     )
 
    second_semester = show_timetable(
        base_queryset.filter(semester__semester_type='SECOND')
    )
    context = {
        "student": student,
        "first_semester_timetable": first_semester.items(),
        "second_semester_timetable": second_semester.items(),
    }

    return render(request, 'management_apps/timetable.html', context)

def show_results(request):
    student = request.user.student
    base_queryset = Result.objects.filter(
        department=student.department,
        level=student.level,
        is_published = True
    ).select_related('student','course','department','level','semester','academic_session','approved_by')
    
    first_semester = base_queryset.filter(semester__semester_type='FIRST')
     
    second_semester = base_queryset.filter(semester__semester_type='SECOND')
    pprint(first_semester)
    pprint(first_semester)
    pprint(f"First : {calculate_gpa(first_semester)}")
    pprint(f"Second : {calculate_gpa(second_semester)}")
    context = {
        'first_semester_gpa' : calculate_gpa(first_semester),
        'second_semester_gpa' : calculate_gpa(second_semester),
        "student": student,
        "first_semester_timetable": first_semester,
        "second_semester_timetable": second_semester,
    }
    return render(request, 'management_apps/result.html', context)
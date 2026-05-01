from django.shortcuts import render
from django.http import HttpResponse
from .models import Timetable,Result
from collections import defaultdict
from pprint import pprint
from django.db.models import Avg, Sum, Count
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

from django.db.models import Avg
from pprint import pprint

def show_results(request):
    student = request.user.student

    # Average GPA (overall)
    avg_gpa = Result.objects.filter(
        department=student.department,
        level=student.level,
        is_published=True
    ).aggregate(average_gpa=Avg('grade_point'))['average_gpa']

    # Base queryset
    base_queryset = Result.objects.filter(
        department=student.department,
        level=student.level,
        is_published=True
    ).select_related(
        'student', 'course', 'department',
        'level'
    )

    # Split semesters
    first_semester = base_queryset.filter(semester__semester_type='FIRST')
    second_semester = base_queryset.filter(semester__semester_type='SECOND')

    # Calculate GPA once
    first_gpa = calculate_gpa(first_semester)
    second_gpa = calculate_gpa(second_semester)
    context = {
        'first_semester_gpa': first_gpa,
        'second_semester_gpa': second_gpa,
        'avg_gpa': avg_gpa,
        "student": student,
        "first_semester_timetable": first_semester,
        "second_semester_timetable": second_semester,
    }

    return render(request, 'management_apps/result.html', context)
from django.contrib import admin # type: ignore
from .models import (
    Faculty, Department, Level, AcademicSession, Semester,
    Lecturer, Venue, Timetable,
    GradingSystem, Result, Complaint, StudentAcademicSummary
)


# ============================================
# FACULTY ADMIN
# ============================================
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)


# ============================================
# DEPARTMENT ADMIN
# ============================================
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty', 'created_at')
    list_filter = ('faculty',)
    search_fields = ('name', 'code')
    ordering = ('code',)
    autocomplete_fields = ['faculty']


# ============================================
# LEVEL ADMIN
# ============================================

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')
    ordering = ('number',)
    search_fields = ('name', 'number')  # <-- ADD THIS


# ============================================
# ACADEMIC SESSION ADMIN
# ============================================
@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('name',)
    ordering = ('-start_date',)


# ============================================
# SEMESTER ADMIN
# ============================================
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'semester_type', 'is_active', 'start_date')
    list_filter = ('semester_type', 'is_active')
    search_fields = ('session__name',)
    autocomplete_fields = ['session']




# ============================================
# LECTURER ADMIN
# ============================================
@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'full_name', 'email', 'user','department', 'is_active')
    list_filter = ('department', 'is_active', 'title')
    search_fields = ('staff_id', 'name', 'email')
    autocomplete_fields = ['department']


# ============================================
# VENUE ADMIN
# ============================================
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_lab', 'has_projector')
    list_filter = ('is_lab', 'has_projector')
    search_fields = ('name',)


# ============================================
# TIMETABLE ADMIN
# ============================================
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('course', 'lecturer', 'venue', 'day', 'start_time', 'end_time')
    list_filter = ('day', 'semester')
    search_fields = ('course__code', 'lecturer__name', 'venue__name')
    autocomplete_fields = ['course', 'lecturer', 'venue', 'semester']
    ordering = ('day', 'start_time')


# ============================================
# GRADING SYSTEM ADMIN
# ============================================
@admin.register(GradingSystem)
class GradingSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'min_score', 'max_score', 'grade_point', 'is_active')
    list_filter = ('name', 'is_active')
    search_fields = ('name', 'grade')
    ordering = ('name', '-min_score')


# ============================================
# RESULT ADMIN
# ============================================
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'course', 'semester',
        'total_score', 'grade', 'grade_point',
        'is_published'
    )

    list_filter = (
        'semester',
        'academic_session',
        'is_published',
        'grade'
    )

    search_fields = (
        'student__first_name',
        'student__last_name',
        'student__registration_number',
        'course__code'
    )

    autocomplete_fields = [
        'student', 'course', 'semester',
        'academic_session', 'approved_by'
    ]

    readonly_fields = (
        'total_score', 'grade', 'grade_point',
        'semester_gpa', 'cumulative_gpa',
        'created_at', 'updated_at'
    )

    ordering = ('-created_at',)


# ============================================
# COMPLAINT ADMIN
# ============================================
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'student', 'complaint_type',
        'priority', 'status', 'created_at'
    )

    list_filter = (
        'status',
        'priority',
        'complaint_type'
    )

    search_fields = (
        'student__first_name',
        'student__last_name',
        'subject'
    )

    autocomplete_fields = [
        'student',
        'course',
        'assigned_to',
        'resolved_by'
    ]

    readonly_fields = ('created_at', 'updated_at')

    ordering = ('-created_at',)


# ============================================
# STUDENT ACADEMIC SUMMARY ADMIN
# ============================================
@admin.register(StudentAcademicSummary)
class StudentAcademicSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'current_cgpa',
        'current_level',
        'total_credits_earned',
        'total_courses_passed',
        'total_courses_failed'
    )

    search_fields = (
        'student__first_name',
        'student__last_name',
        'student__registration_number'
    )

    autocomplete_fields = ['student', 'current_level']

    readonly_fields = ('last_updated',)

    ordering = ('-current_cgpa',)


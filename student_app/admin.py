from django.contrib import admin # type: ignore
from .models import Student,Registration,Session,Course,Complaint

# ================================
# STUDENT ADMIN
# ================================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    # Fields to display in admin list
    list_display = (
        'first_name',
        'second_name',
        'email',
        'registration_number',
        'gender',
        'level',
        'department',
        'session',
        'date_registered',
       
    ) 

    # Add filters on the right side
    list_filter = (
        'gender',
        'level',
        'faculty',
        'department',
        'session',
        'date_registered'
    )

    # Search functionality
    search_fields = (
        'registration_number',
        'user'
    )

    # Default ordering
    ordering = ('-date_registered',)

    # Make fields clickable
    list_display_links = (
        'registration_number',
        'first_name',
        'second_name',
      
    )

    # Read-only fields
    readonly_fields = ('date_registered',)

    # Field grouping (very clean UI)
    fieldsets = (
        ("Personal Information", {
            'fields': (
            'first_name',
            'second_name',
            'last_name',
            'email',
            'gender',
            'blood_group',
            'image',
            'user'
                
            )
        }),
        ("Academic Information", {
            'fields': (
                'registration_number',
                'level',
                'faculty',
                'department',
                'session'
            )
        }),
        ("Metadata", {
            'fields': ('date_registered',)
        }),
    )



# ================================
# COURSE ADMIN
# ================================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'code',
        'date_created',
        'unit',
        'is_active'
    )

    list_filter = (
        'depertiment',
        'level',
    )
    
    search_fields = (
        'title',
        'code'
    )

    ordering = ('-date_created',)
    
    search_fields = ('title',)
    readonly_fields = ('date_created',)


# ================================
# ENROLLMENT ADMIN
# ================================
@admin.register(Registration)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'course',
        'session',
        'date_enrolled'
    )

    list_filter = (
        'session',
        'date_enrolled'
    )

    search_fields = (
        'student__first_name',
        'student__last_name',
        'student__registration_number',
        'course__course_name'
    )

    ordering = ('-date_enrolled',)

    readonly_fields = ('date_enrolled',)

    # Optimize ForeignKey dropdowns (VERY IMPORTANT ⚡)
    autocomplete_fields = ['student', 'course']
    

admin.site.register(Session)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'course',
        'session',
        'complaint_type'
    )

    list_filter = (
        'session',
        'priority',
        'subject'
    )

    search_fields = (
        'student__first_name',
        'student__last_name',
        'student__registration_number',
        'course__course_name'
    )

    ordering = ('-created_at',)

    readonly_fields = ('created_at',)

    # Optimize ForeignKey dropdowns (VERY IMPORTANT ⚡)
    autocomplete_fields = ['student', 'course']
    

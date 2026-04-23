
from django.db import models 
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.db import transaction
from django.contrib.auth.models import User
# ==================== SESSION MODEL ====================
class Session(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="e.g., 2025/2026 Harmattan"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Academic Session"
        verbose_name_plural = "Academic Sessions"

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError(_("End date must be after start date."))

    def save(self, *args, **kwargs):
        # Ensure only one active session
        if self.is_current:
            Session.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)



# ================================
# COURSE MODEL
# ================================


class Course(models.Model):
    faculty = models.ForeignKey('management_app.Faculty',on_delete=models.CASCADE)
    depertiment = models.ForeignKey('management_app.Department',on_delete=models.CASCADE,related_name='courses') 
    level = models.ForeignKey('management_app.Level',on_delete=models.CASCADE,related_name='levels')
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    unit = models.PositiveIntegerField(default=2)
    semester_type = models.CharField(max_length=10, choices=[('FIRST', 'First Semester'),('SECOND', 'Second Semester'),('SUMMER', 'Summer Session'),])
    is_elective = models.BooleanField(default=False)
    is_core = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['code']
        unique_together = ['code', 'semester_type', 'depertiment']  # ✅ Same course code can exist in different depts
    
    def __str__(self):
        return f"{self.code}: {self.title} ({self.unit} units)"


    # def __str__(self):
    #     return f"{self.get_course_name_display()} ({self.get_course_code_display()})"

 
 
 
# ================================
# STUDENT MODEL
# ================================
class Student(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    )

    BLOOD_GROUP_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O')
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default=MALE
    )

    blood_group = models.CharField(
        max_length=2,
        choices=BLOOD_GROUP_CHOICES,
        default='A'
    )
    first_name = models.CharField(max_length=150)
    second_name = models.CharField(max_length=200,blank=True)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    user = models.OneToOneField(User,on_delete=models.CASCADE,null = True,blank = True)
    registration_number = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    # image = models.ImageField(upload_to='students/', null=True, blank=True)

    level = models.ForeignKey('management_app.Level',on_delete=models.CASCADE)
    faculty = models.CharField(max_length=200)
    department = models.ForeignKey('management_app.Department',on_delete=models.CASCADE,related_name='students') 
    session = models.ForeignKey(Session,
                                on_delete=models.SET_NULL,
                                null=True,   # 🔥 TEMP FIX
                                blank=True)

    date_registered = models.DateTimeField(default=timezone.now)
    
    date_of_birth = models.DateField(null=True, blank=True)

    # 🔥 Many-to-Many via Registration (BEST PRACTICE)
    courses = models.ManyToManyField(
        Course,
        through='Registration',
        related_name='students'
    )
    
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.last_name})"

    class Meta:
        ordering = ['date_registered']
        

    # ✅ Helper method (clean API)
    def get_courses_by_session(self, session):
        return self.courses.filter(registrations__session=session)

    def get_current_courses(self):
        current_session = Session.objects.filter(is_current=True).first()
        if not current_session:
            return Course.objects.none()
        return self.get_courses_by_session(current_session)




#     
# ================================
# ENROLLMENT MODEL
# ================================
class Registration(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments"  # clearer than "students"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="registrations"
    )
    date_enrolled = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('dropped', 'Dropped'),
            ('completed', 'Completed'),
        ],
        default='approved'
    )
    def __str__(self):
        return f"{self.student} → {self.course} ({self.session})"
    

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('dropped', 'Dropped'),
            ('completed', 'Completed'),
        ],
        default='approved'
    )
    
    class Meta:
        constraints = [
            # ✅ Modern replacement for unique_together
            models.UniqueConstraint(
                fields=['student', 'course', 'session'],
                name='unique_student_course_session'
            )
        ]
        indexes = [
            models.Index(fields=['student', 'session']),
            models.Index(fields=['session', 'course']),
            models.Index(fields=['status']),
        ]
        ordering = ['-date_enrolled']

    def __str__(self):
        return f"{self.student} - {self.course} ({self.session})"

    def clean(self):
        if not self.course.is_active:
            raise ValidationError(_("This course is not currently active."))

        if self.session.start_date > self.session.end_date:
            raise ValidationError(_("Invalid session dates."))

    def save(self, *args, **kwargs):
        self.full_clean()  # enforce validation
        super().save(*args, **kwargs)
        
def register_courses_for_session(student, course_ids, session):
    """
    Register multiple courses with full validation and feedback.
    """

    if not session:
        raise ValueError("Session is required")

    # ✅ Only active courses
    courses = Course.objects.filter(
        id__in=course_ids,
        is_active=True
    )

    # ✅ Find already registered courses
    existing_course_ids = set(
        Registration.objects.filter(
            student=student,
            session=session,
            course__in=courses
        ).values_list('course_id', flat=True)
    )

    # ✅ Filter new courses only
    new_courses = [c for c in courses if c.id not in existing_course_ids]

    registrations = [
        Registration(
            student=student,
            course=course,
            session=session,
            status='approved'
        )
        for course in new_courses
    ]

    with transaction.atomic():
        created = Registration.objects.bulk_create(registrations)

    return {
        "registered_count": len(created),
        "already_registered": list(existing_course_ids),
        "new_registered_ids": [c.id for c in new_courses]
    }


class Student_Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        
        ('PENDING', 'Pending Review'),
        ('IN_REVIEW', 'Under Review'),
        ('ESCALATED', 'Escalated to HOD'),
        ('RESOLVED', 'Resolved'),
        ('REJECTED', 'Rejected'),
        ('CLOSED', 'Closed'),
    ]
    
    COMPLAINT_TYPES = [
        
        ('RESULT', 'Result Discrepancy'),
        ('COURSE', 'Course Registration Issue'),
        ('SCHEDULE', 'Schedule Conflict'),
        ('LECTURER', 'Lecturer Concern'),
        ('OTHER', 'Other Academic Issue'),
    ]
    
    student_name = models.ForeignKey(Student,
        on_delete=models.CASCADE,
        related_name='complaints'
    )
    course_name = models.ForeignKey(Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )
    complaint_type_status = models.CharField(max_length=20, choices=COMPLAINT_TYPES)
    subject_name = models.CharField(max_length=200)
    description_status = models.TextField()
    priority_type = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status_type = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    # Timestamps
    created_at_date = models.DateTimeField(auto_now_add=True)
    updated_at_date = models.DateTimeField(auto_now=True)
    




# # ================================
# # RESULT MODEL - COMPLETELY REWRITTEN
# # ================================
# class Result(models.Model):
#     FIRST_SEMESTER = 'FS'
#     SECOND_SEMESTER = 'SS'

#     SEMESTER_CHOICES = (
#         (FIRST_SEMESTER, "First Semester"),
#         (SECOND_SEMESTER, "Second Semester")
#     )

#     # Grade-based remarks (auto-calculated)
#     REMARK_CHOICES = (
#         ('FL', 'Fail'),
#         ('PR', 'Poor'),
#         ('PS', 'Pass'),
#         ('GD', 'Good'),
#         ('VG', 'Very Good'),
#         ('EX', 'Excellent'),
#     )

#     # Core relationships
#     student = models.ForeignKey(
#         Student,
#         on_delete=models.CASCADE,
#         related_name="results"
#     )

#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="results"
#     )
    
#     enrollment = models.ForeignKey(
#         Enrollment,
#         on_delete=models.CASCADE,
#         related_name="results",
#         null=True,
#         blank=True
#     )

#     # Scores (only these need to be entered)
#     ca_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         validators=[MinValueValidator(0), MaxValueValidator(40)],
#         help_text="Continuous Assessment (max 40)"
#     )
    
#     exam_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         validators=[MinValueValidator(0), MaxValueValidator(60)],
#         help_text="Exam Score (max 60)"
#     )

#     # Auto-calculated fields
#     total_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         editable=False,
#         null=True,
#         blank=True
#     )
    
#     grade = models.CharField(
#         max_length=2,
#         editable=False,
#         null=True,
#         blank=True
#     )
    
#     grade_point = models.DecimalField(
#         max_digits=4,
#         decimal_places=2,
#         editable=False,
#         null=True,
#         blank=True
#     )
    
#     # GPA and CGPA (auto-calculated)
#     semester_gpa = models.DecimalField(
#         max_digits=4,
#         decimal_places=2,
#         editable=False,
#         null=True,
#         blank=True
#     )
    
#     cumulative_gpa = models.DecimalField(
#         max_digits=4,
#         decimal_places=2,
#         editable=False,
#         null=True,
#         blank=True
#     )

#     # Remark (auto-calculated from grade)
#     remark = models.CharField(
#         max_length=2,
#         choices=REMARK_CHOICES,
#         editable=False,
#         null=True,
#         blank=True
#     )

#     # Optional manual comment
#     comment = models.TextField(blank=True, null=True)

#     # Metadata
#     semester = models.CharField(
#         max_length=2,
#         choices=SEMESTER_CHOICES,
#         default=FIRST_SEMESTER
#     )
    
#     session = models.CharField(max_length=20)
#     is_published = models.BooleanField(default=False)
#     date_released = models.DateTimeField(default=timezone.now)
    
#     class Meta:
#         unique_together = ['student', 'course', 'semester', 'session']
#         ordering = ['-date_released']
#         indexes = [
#             models.Index(fields=['student', 'semester', 'session']),
#             models.Index(fields=['course', 'is_published']),
#         ]

#     def save(self, *args, **kwargs):
#         """Auto-calculate everything before saving"""
        
#         # 1. Calculate total score
#         self.total_score = self.ca_score + self.exam_score
        
#         # 2. Calculate grade and grade point
#         if self.total_score >= 70:
#             self.grade = 'A'
#             self.grade_point = Decimal('5.00')
#             self.remark = 'EX'  # Excellent
#         elif self.total_score >= 60:
#             self.grade = 'B'
#             self.grade_point = Decimal('4.00')
#             self.remark = 'VG'  # Very Good
#         elif self.total_score >= 50:
#             self.grade = 'C'
#             self.grade_point = Decimal('3.00')
#             self.remark = 'GD'  # Good
#         elif self.total_score >= 45:
#             self.grade = 'D'
#             self.grade_point = Decimal('2.00')
#             self.remark = 'PS'  # Pass
#         elif self.total_score >= 40:
#             self.grade = 'E'
#             self.grade_point = Decimal('1.00')
#             self.remark = 'PR'  # Poor
#         else:
#             self.grade = 'F'
#             self.grade_point = Decimal('0.00')
#             self.remark = 'FL'  # Fail
        
#         # 3. Save first to have an ID
#         super().save(*args, **kwargs)
        
#         # 4. Calculate GPA and CGPA for this student/semester
#         self.calculate_gpa_cgpa()
    
#     def calculate_gpa_cgpa(self):
#         """Calculate semester GPA and cumulative CGPA"""
#         from django.db.models import Sum, F
        
#         # Get all published results for this student in this semester
#         semester_results = Result.objects.filter(
#             student=self.student,
#             semester=self.semester,
#             session=self.session,
#             is_published=True
#         )
        
#         if semester_results.exists():
#             # Calculate total quality points and credits for semester
#             total_quality_points = 0
#             total_credits = 0
            
#             for result in semester_results:
#                 total_quality_points += float(result.grade_point) * result.course.credit_hours
#                 total_credits += result.course.credit_hours
            
#             # Calculate semester GPA
#             if total_credits > 0:
#                 self.semester_gpa = Decimal(str(round(total_quality_points / total_credits, 2)))
#             else:
#                 self.semester_gpa = Decimal('0.00')
#         else:
#             self.semester_gpa = Decimal('0.00')
        
#         # Calculate CGPA (all semesters)
#         all_results = Result.objects.filter(
#             student=self.student,
#             is_published=True
#         )
        
#         if all_results.exists():
#             total_quality_points_all = 0
#             total_credits_all = 0
            
#             for result in all_results:
#                 total_quality_points_all += float(result.grade_point) * result.course.credit_hours
#                 total_credits_all += result.course.credit_hours
            
#             if total_credits_all > 0:
#                 self.cumulative_gpa = Decimal(str(round(total_quality_points_all / total_credits_all, 2)))
#             else:
#                 self.cumulative_gpa = Decimal('0.00')
#         else:
#             self.cumulative_gpa = Decimal('0.00')
        
#         # Update all results for this semester with same GPA
#         Result.objects.filter(
#             student=self.student,
#             semester=self.semester,
#             session=self.session,
#             is_published=True
#         ).update(
#             semester_gpa=self.semester_gpa,
#             cumulative_gpa=self.cumulative_gpa
#         )
    
#     @property
#     def get_grade_letter(self):
#         """Return letter grade"""
#         return self.grade
    
#     @property
#     def get_remark_display_text(self):
#         """Return readable remark"""
#         remark_dict = dict(self.REMARK_CHOICES)
#         return remark_dict.get(self.remark, 'N/A')
    
#     def __str__(self):
#         return f"{self.student} - {self.course}: {self.grade} ({self.total_score})"


# # ================================
# # STUDENT ACADEMIC SUMMARY (Helper Model)
# # ================================
# class StudentAcademicSummary(models.Model):
#     """Store current academic standing for each student"""
    
#     student = models.OneToOneField(
#         Student,
#         on_delete=models.CASCADE,
#         related_name='academic_summary'
#     )
    
#     current_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
#     current_level = models.PositiveSmallIntegerField(default=100)
#     total_credits_earned = models.PositiveIntegerField(default=0)
#     total_courses_passed = models.PositiveIntegerField(default=0)
#     total_courses_failed = models.PositiveIntegerField(default=0)
#     last_updated = models.DateTimeField(auto_now=True)
    
#     def update_from_results(self):
#         """Update summary based on all published results"""
#         from django.db.models import Sum, Count, Q
        
#         results = Result.objects.filter(
#             student=self.student,
#             is_published=True
#         )
        
#         if results.exists():
#             # Calculate total credits
#             self.total_credits_earned = sum(
#                 r.course.credit_hours for r in results if r.grade != 'F'
#             )
            
#             # Count passes and failures
#             self.total_courses_passed = results.filter(~Q(grade='F')).count()
#             self.total_courses_failed = results.filter(grade='F').count()
            
#             # Get latest CGPA
#             latest_result = results.order_by('-date_released').first()
#             if latest_result:
#                 self.current_cgpa = latest_result.cumulative_gpa
        
#         self.save()
    
#     def __str__(self):
#         return f"{self.student} - CGPA: {self.current_cgpa}"

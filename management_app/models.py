from django.db import models # type: ignore

# Create your models here.
# models.py - COMPLETE FIXED VERSION

from django.db import models # type: ignore
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError # type: ignore
from django.utils import timezone  # type: ignore # ✅ FIXED: correct import
from decimal import Decimal
from django.contrib.auth.models import User

# ============================================
# CORE ACADEMIC STRUCTURE
# ============================================

class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    logo = models.ImageField(upload_to='faculty/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.name[:3].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logo = models.ImageField(upload_to='depertiment/', null=True, blank=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Level(models.Model):
    """Academic level (100, 200, 300, 400, 500)"""
    number = models.PositiveSmallIntegerField(unique=True)  # 100, 200, etc.
    name = models.CharField(max_length=50)  # "100 Level", "200 Level", etc.
    
    def save(self, *args, **kwargs):
        self.name = f"{self.number} Level"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class AcademicSession(models.Model):
    """Academic session (e.g., 2023/2024)"""
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
    
    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicSession.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Semester(models.Model):
    """Semester within an academic session"""
    SESSION_TYPE = [
        ('FIRST', 'First Semester'),
        ('SECOND', 'Second Semester'),
        ('SUMMER', 'Summer Session'),
    ]
    
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='semesters')
    semester_type = models.CharField(max_length=10, choices=SESSION_TYPE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['session', 'semester_type']
        ordering = ['session', 'start_date']
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Only one active semester per session
            Semester.objects.filter(session=self.session, is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.session} - {self.get_semester_type_display()}"
    
    def __str__(self):
        return self.full_name

# ============================================
# COURSE & LECTURER MANAGEMENT
# ============================================


class Lecturer(models.Model):
    TITLE_CHOICES = [
        ('PROF', 'Professor'),
        ('DR', 'Doctor'),
        ('MR', 'Mr.'),
        ('MRS', 'Mrs.'),
        ('MS', 'Ms.'),
        ('ENGR', 'Engineer'),
        ('ARCH', 'Architect'),
    ]
    
    staff_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES)
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User,on_delete=models.CASCADE,null = True,blank = True)
    image = models.ImageField(upload_to='lecturers/', blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    roll = models.CharField(max_length=255, blank=True,null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='lecturers')
    specialization = models.CharField(max_length=200, blank=True)
    max_workload_hours = models.PositiveSmallIntegerField(default=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def full_name(self):
        return f"{self.get_title_display()} {self.name}"
    
    def __str__(self):
        return f"{self.full_name} ({self.staff_id})"

class Venue(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    has_projector = models.BooleanField(default=False)
    is_lab = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"

class Timetable(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]
    
    course = models.ForeignKey('student_app.Course', on_delete=models.CASCADE, related_name='schedules')
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='schedules')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='schedules')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='schedules')  # ✅ Added semester context
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    level = models.ForeignKey(Level,on_delete=models.SET_NULL,null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ['venue', 'day', 'start_time', 'semester']
        ordering = ['day', 'start_time']
        indexes = [
            models.Index(fields=['semester', 'day']),
            models.Index(fields=['lecturer', 'semester']),
        ]

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")
        
        duration = (self.end_time.hour * 60 + self.end_time.minute) - \
                   (self.start_time.hour * 60 + self.start_time.minute)
        if duration < 45:
            raise ValidationError("Schedule slot must be at least 45 minutes")
        if duration > 180:
            raise ValidationError("Schedule slot cannot exceed 3 hours")
    
    def __str__(self):
        return f"{self.course.code} - {self.get_day_display()} {self.start_time}-{self.end_time} @ {self.venue.name}"

# ============================================
# GRADING & RESULTS SYSTEM (FIXED)
# ============================================

class GradingSystem(models.Model):
    """Configurable grading scale"""
    name = models.CharField(max_length=50)  # e.g., "Undergraduate Scale"
    grade = models.CharField(max_length=2)  # A, B, C, etc.
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    description = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)  # ✅ Added active flag
    
    class Meta:
        unique_together = ['name', 'grade']
        ordering = ['name', '-min_score']
    
    def __str__(self):
        return f"{self.name}: {self.grade} ({self.min_score}-{self.max_score} points: {self.grade_point})"

class Result(models.Model):
    """
    Student result with automatic grade calculation
    """
    # Core relationships
    student = models.ForeignKey('student_app.Student',on_delete=models.CASCADE,related_name='results')
    course = models.ForeignKey('student_app.Course',on_delete=models.CASCADE, related_name='results')
    
    # ✅ ADDED missing fields
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='results'
    )
    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    # Scores (only these need manual entry)
    continuous_assessment = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(40)]
    )
    exam_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(60)]
    )
    
    # Auto-calculated fields
    total_score = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    grade = models.CharField(max_length=2, editable=False)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, editable=False)
    
    # ✅ ADDED GPA fields
    semester_gpa = models.DecimalField(max_digits=4, decimal_places=2, editable=False, null=True)
    cumulative_gpa = models.DecimalField(max_digits=4, decimal_places=2, editable=False, null=True)
    
    # Workflow
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        Lecturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_results'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # ✅ FIXED: Now semester field exists
        unique_together = ['student', 'course', 'semester']
        indexes = [
            models.Index(fields=['student', 'semester', 'is_published']),
            models.Index(fields=['course', 'is_published']),
            models.Index(fields=['student', 'cumulative_gpa']),
        ]
        
    def clean(self):
        if self.continuous_assessment + self.exam_score > 100:
            raise ValidationError("Total score cannot exceed 100")
    
    def save(self, *args, **kwargs):
        # Calculate total
        self.total_score = self.continuous_assessment + self.exam_score
        
        # Get grade from grading system
        grading_system = GradingSystem.objects.filter(
            name='Undergraduate Scale',
            min_score__lte=self.total_score,
            max_score__gte=self.total_score,
            is_active=True
        ).first()
        
        if grading_system:
            self.grade = grading_system.grade
            self.grade_point = grading_system.grade_point
        else:
            # Fallback grading
            if self.total_score >= 70:
                self.grade = 'A'
                self.grade_point = 5.00
            elif self.total_score >= 60:
                self.grade = 'B'
                self.grade_point = 4.00
            elif self.total_score >= 50:
                self.grade = 'C'
                self.grade_point = 3.00
            elif self.total_score >= 45:
                self.grade = 'D'
                self.grade_point = 2.00
            elif self.total_score >= 40:
                self.grade = 'E'
                self.grade_point = 1.00
            else:
                self.grade = 'F'
                self.grade_point = 0.00
        
        super().save(*args, **kwargs)
        
        # Update GPA after saving
        self.update_gpa()
    
    def update_gpa(self):
        """Calculate semester GPA and CGPA"""
        # Get all published results for this semester
        semester_results = Result.objects.filter(
            student=self.student,
            semester=self.semester,
            is_published=True
        )
        
        if semester_results.exists():
            total_points = 0
            total_units = 0
            
            for result in semester_results:
                total_points += float(result.grade_point) * result.course.unit
                total_units += result.course.unit
            
            if total_units > 0:
                semester_gpa = round(total_points / total_units, 2)
            else:
                semester_gpa = 0.00
        else:
            semester_gpa = 0.00
        
        # Calculate CGPA (all semesters)
        all_results = Result.objects.filter(
            student=self.student,
            is_published=True
        )
        
        if all_results.exists():
            total_points_all = 0
            total_units_all = 0
            
            for result in all_results:
                total_points_all += float(result.grade_point) * result.course.unit
                total_units_all += result.course.unit
            
            if total_units_all > 0:
                cgpa = round(total_points_all / total_units_all, 2)
            else:
                cgpa = 0.00
        else:
            cgpa = 0.00
        
        # Update all results in this semester with same GPA
        Result.objects.filter(
            student=self.student,
            semester=self.semester,
            is_published=True
        ).update(
            semester_gpa=semester_gpa,
            cumulative_gpa=cgpa
        )
    
    def __str__(self):
        return f"{self.student} - {self.course.code}: {self.grade} ({self.total_score}%)"

# ============================================
# COMPLAINT MANAGEMENT
# ============================================

class Complaint(models.Model):
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
    
    student = models.ForeignKey('student_app.Student',
        on_delete=models.CASCADE,
        related_name='complaints'
    )
    course = models.ForeignKey('student_app.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )
    complaint_type = models.CharField(max_length=20, choices=COMPLAINT_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Resolution tracking
    assigned_to = models.ForeignKey(
        Lecturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        Lecturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_complaints'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['student', 'status']),
        ]
    
    def resolve(self, lecturer, resolution_notes):
        self.status = 'RESOLVED'
        self.resolution_notes = resolution_notes
        self.resolved_by = lecturer
        self.resolved_at = timezone.now()
        self.save()
    
    def escalate(self):
        if self.status == 'IN_REVIEW':
            self.status = 'ESCALATED'
            self.priority = 'HIGH'
            self.save()
    
    def __str__(self):
        return f"Complaint #{self.id}: {self.student} - {self.subject[:50]}"

# ============================================
# ✅ ADD THIS: Student Academic Summary
# ============================================

class StudentAcademicSummary(models.Model):
    """Denormalized student academic record for quick access"""
    
    student = models.OneToOneField(
        'student_app.Student',
        on_delete=models.CASCADE,
        related_name='academic_summary'
    )
    
    current_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    current_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    total_credits_earned = models.PositiveIntegerField(default=0)
    total_courses_passed = models.PositiveIntegerField(default=0)
    total_courses_failed = models.PositiveIntegerField(default=0)
    total_courses_taken = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Student Academic Summary"
        verbose_name_plural = "Student Academic Summaries"
    
    def update_from_results(self):
        """Update summary based on all published results"""
        results = Result.objects.filter(
            student=self.student,
            is_published=True
        ).select_related('course')
        
        if results.exists():
            # Calculate credits
            self.total_credits_earned = sum(
                r.course.unit for r in results if r.grade != 'F'
            )
            
            # Count passes and failures
            self.total_courses_passed = results.exclude(grade='F').count()
            self.total_courses_failed = results.filter(grade='F').count()
            self.total_courses_taken = results.count()
            
            # Get latest CGPA
            latest_result = results.order_by('-created_at').first()
            if latest_result and latest_result.cumulative_gpa:
                self.current_cgpa = latest_result.cumulative_gpa
            
            # Determine current level (simplified)
            if self.total_credits_earned >= 360:
                level_num = 500
            elif self.total_credits_earned >= 270:
                level_num = 400
            elif self.total_credits_earned >= 180:
                level_num = 300
            elif self.total_credits_earned >= 90:
                level_num = 200
            else:
                level_num = 100
            
            self.current_level = Level.objects.filter(number=level_num).first()
        
        self.save()
    
    def __str__(self):
        return f"{self.student} - CGPA: {self.current_cgpa}"
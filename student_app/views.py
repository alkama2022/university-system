from django.shortcuts import render,redirect, get_object_or_404
from .forms import ComplaintForm
from .models import Registration,Student,Course,Session
from django.contrib import messages
from django.db.models import Prefetch
from django.core.paginator import Paginator
from management_app.models import Faculty,Department,Lecturer
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required

def complaint_list(request):
    student = request.user.student
    complaints = student.complaints.select_related('course').all()
    context = {'complaints': complaints}
    return render(request, 'complaint_list.html', context)
@login_required
def create_complaint(request):
    student = request.user.student

    if request.method == 'POST':
        form = ComplaintForm(request.POST, student=student)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = student
            complaint.save()
            messages.success(request, "Complaint submitted successfully")
            return redirect('student_app:dashboard')
        messages.error(request, "Please correct the errors below")
        return render(request, 'complaint_form.html', {'form': form})
    else:
        form = ComplaintForm(student=student)

    return render(request, 'complaint_form.html', {'form': form})

@login_required
def student_propile(request):
    student = Student.objects.get(user = request.user)
    context = {'student':student}
    return render(request,'profile.html',context)

@login_required
def show_depertment(request,dept_id):
    """Display department details with staff and courses"""
    department = get_object_or_404(
        Department.objects.prefetch_related('lecturers', 'courses'),
        pk=dept_id
    )

    # Get all courses for this department, ordered by level
    lecturers = Lecturer.objects.filter(
        department=department,
        is_active=True
    ).order_by('roll', 'name')
    
    courses = Course.objects.filter(
        depertiment=department,
        is_active=True
    ).select_related('depertiment').order_by('level', 'code')

    context = {
        'department': department,
        'lecturers': lecturers,
        'courses': courses,
    }
    return render(request,'depertment.html',context)


@login_required
def home(request):
    selected_faculty = Faculty.objects.prefetch_related('departments').first()
    return render(request,'home.html',{'selected_faculty':selected_faculty})


MAX_UNITS = 40

@login_required
def enrollment_view(request):
    try:
      student = request.user.student
    except Student.DoesNotExist:
        messages.error(request,"You Are Not Authorize Student To Enter This Site")
        return redirect('student_app:home')
    session = Session.objects.get(is_active=True)
    # semester = Semester.objects.get(is_active=True)

    courses = Course.objects.filter(
        depertiment=student.department,
        level=student.level
    )

    if request.method == "POST":
        selected_courses = request.POST.getlist('courses')

        if not selected_courses:
            messages.error(request, "No course selected")
            return redirect('student_app:enrollment')

        enrollments = Registration.objects.filter(
            student=student,
            session=session,
            # semester=semester
        )

        current_units = sum(e.course.unit for e in enrollments)

        total_new_units = 0
        courses_to_add = []

        for course_id in selected_courses:
            course = Course.objects.get(id=course_id)

            # جلوگیری duplicate
            exists = Registration.objects.filter(
                student=student,
                course=course,
                session=session,
            ).exists()

            if not exists:
                total_new_units += course.unit
                courses_to_add.append(course)

        # 🚫 Check unit limit
        if current_units + total_new_units > MAX_UNITS:
            messages.error(request, "Unit limit exceeded")
            return redirect('student_app:enrollment')

        # ✅ Save all at once
        for course in courses_to_add:
            Registration.objects.create(
                student=student,
                course=course,
                session=session,
                # semester=semester
            )

        messages.success(request, "Courses registered successfully")
        return redirect('student_app:dashboard')

    return render(request, 'enrollment.html', {
        'courses': courses
    })
    
@login_required  
def show_student(request):
    students = Student.objects.all()
    paginator = Paginator(students, 6)  # 10 students per page

    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)

    context = {
        'students':students
    }
    return render(request,'student_lists.html',context)

@login_required
def student_details(request, pk):
    student_details = Student.objects.prefetch_related(
        Prefetch(
            'enrollments',
            queryset=Registration.objects.select_related('course')  # fetch course in the same query
        )
    ).get(id=pk)
    context = {'student_details': student_details}
    return render(request, 'student_details.html', context)




@login_required
def student_details(request, pk):
    """Function-based view with pagination"""
    student = get_object_or_404(
        Student.objects.prefetch_related('enrollments__course'),
        pk=pk
    )
    
    # Get all enrollments
    # enrollments = student.enrollments.select_related('course').all()
    enrollments = student.enrollments.all()  # ✅ USE PREFETCH CACHE
    context = {
        'student': student,
        'total_credits': sum(e.course.unit for e in enrollments),
        'total_courses': enrollments.count(),
    }
    
    return render(request, 'student_details.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = authenticate(request, username=username, password=password,email = email)
        if user:
            login(request, user)
            return redirect('student_app:home')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('student_app:login')

    return render(request, 'logout.html')
    
    
@login_required
def dashboard(request):
    student = request.user.student

    return render(request, 'dashboard.html', {
        'student': student
    })
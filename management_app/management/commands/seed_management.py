from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
from random import randint, choice
import uuid

from management_app.models import *
from student_app.models import *

fake = Faker()

BATCH_SIZE = 1000


class Command(BaseCommand):
    help = "Fast bulk seeding for university system"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Seeding started...")

        with transaction.atomic():
            self.create_faculties(10)
            self.create_departments(30)
            self.create_levels()
            self.create_sessions(5)
            self.create_users(1000)
            self.create_lecturers(500)
            self.create_students(5000)
            self.create_courses(2000)
            self.create_complaints(3000)

        self.stdout.write(self.style.SUCCESS("✅ Seeding completed successfully"))

    # =========================
    # FACULTY
    # =========================
    def create_faculties(self, n):
        objs = [
            Faculty(
                name=f"{fake.unique.company()} Faculty",
                code=fake.unique.bothify(text="FAC###")
            )
            for _ in range(n)
        ]
        Faculty.objects.bulk_create(objs, ignore_conflicts=True)

    # =========================
    # DEPARTMENT
    # =========================
    def create_departments(self, n):
        faculties = list(Faculty.objects.all())
        objs = [
            Department(
                name=fake.unique.job(),
                code=fake.unique.bothify("DEP###"),
                faculty=choice(faculties)
            )
            for _ in range(n)
        ]
        Department.objects.bulk_create(objs, ignore_conflicts=True)

    # =========================
    # LEVELS
    # =========================
    def create_levels(self):
        levels = [
            Level(number=100),
            Level(number=200),
            Level(number=300),
            Level(number=400),
            Level(number=500),
        ]
        Level.objects.bulk_create(levels, ignore_conflicts=True)

    # =========================
    # SESSIONS
    # =========================
    def create_sessions(self, n):
        objs = []
        for i in range(n):
            year = 2020 + i
            objs.append(Session(
                name=f"{year}/{year+1}",
                start_date=fake.date_this_decade(),
                end_date=fake.date_this_decade(),
                is_current=(i == n-1)
            ))
        Session.objects.bulk_create(objs, ignore_conflicts=True)

    # =========================
    # USERS
    # =========================
    def create_users(self, n):
        objs = []
        for i in range(n):
            username = f"user_{uuid.uuid4().hex[:10]}"
            objs.append(User(
                username=username,
                email=fake.unique.email()
            ))
        User.objects.bulk_create(objs, ignore_conflicts=True)

    # =========================
    # LECTURERS (FIXED UNIQUE ERROR)
    # =========================
    def create_lecturers(self, n):
        departments = list(Department.objects.all())
        objs = []

        for i in range(n):
            objs.append(Lecturer(
                staff_id=f"STAFF-{uuid.uuid4().hex[:8]}",  # FIX UNIQUE
                title=choice(["DR", "PROF", "MR", "MRS"]),
                name=fake.name(),
                email=f"lecturer_{uuid.uuid4().hex[:10]}@school.edu",  # FIX UNIQUE
                department=choice(departments) if departments else None
            ))

        Lecturer.objects.bulk_create(objs, ignore_conflicts=True)

    # =========================
    # STUDENTS (FIXED EMPTY ERROR)
    # =========================
    def create_students(self, n):
        users = list(User.objects.all())
        levels = list(Level.objects.all())
        departments = list(Department.objects.all())
        sessions = list(Session.objects.all())

        if not (users and levels and departments and sessions):
            self.stdout.write("❌ Missing base data")
            return

        objs = []
        for i in range(n):
            objs.append(Student(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                registration_number=f"REG-{uuid.uuid4().hex[:10]}",
                user=choice(users),
                level=choice(levels),
                department=choice(departments),
                session=choice(sessions),
            ))

        Student.objects.bulk_create(objs, ignore_conflicts=True)

    # =========================
    # COURSES
    # =========================
    def create_courses(self, n):
        faculties = list(Faculty.objects.all())
        departments = list(Department.objects.all())
        levels = list(Level.objects.all())

        objs = [
            Course(
                faculty=choice(faculties),
                depertiment=choice(departments),
                level=choice(levels),
                title=fake.sentence(nb_words=3),
                code=f"CSC{uuid.uuid4().hex[:5].upper()}",
                unit=choice([1, 2, 3]),
                semester_type=choice(["FIRST", "SECOND"])
            )
            for _ in range(n)
        ]

        Course.objects.bulk_create(objs, ignore_conflicts=True)

    # =========================
    # COMPLAINTS
    # =========================
    def create_complaints(self, n):
        students = list(Student.objects.all())
        courses = list(Course.objects.all())

        if not students or not courses:
            self.stdout.write("❌ No students or courses available")
            return

        objs = [
            Complaint(
                student=choice(students),
                course=choice(courses),
                complaint_type=choice(["RESULT", "COURSE", "SCHEDULE"]),
                subject=fake.sentence(nb_words=6),
                description=fake.text()
            )
            for _ in range(n)
        ]

        Complaint.objects.bulk_create(objs, ignore_conflicts=True)
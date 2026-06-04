from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
from random import choice, randint, sample
from student_app.models import (
    Session, Course, Student, Registration, Complaint
)

fake = Faker()

BATCH_SIZE = 1000   # ⚡ important for performance


class Command(BaseCommand):
    help = "High-performance database seeder (10k–100k records)"

    def handle(self, *args, **kwargs):

        self.stdout.write("Starting seeding...")

        self.create_session()
        self.create_students(10000)      # 🔥 change to 50000 or 100000
        self.create_registrations()
        self.create_complaints(5000)

        self.stdout.write(self.style.SUCCESS("DONE SEEDING 🚀"))

    # =========================
    # SESSION
    # =========================
    def create_session(self):
        Session.objects.get_or_create(
            name="2025/2026 Harmattan",
            defaults={
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "is_current": True,
                "is_active": True,
            }
        )

    # =========================
    # STUDENTS (FAST BULK)
    # =========================
    def create_students(self, total):

        users = []
        students = []

        session = Session.objects.first()
        courses = list(Course.objects.all())

        for i in range(total):

            first = fake.first_name()
            last = fake.last_name()

            user = User(
                username=f"{first.lower()}{i}",
                email=fake.email(),
            )
            user.set_password("password123")
            users.append(user)

        # BULK CREATE USERS
        User.objects.bulk_create(users, batch_size=BATCH_SIZE)

        created_users = User.objects.all().order_by('-id')[:total]

        for i, user in enumerate(created_users):

            dept = fake.word()

            students.append(
                Student(
                    first_name=fake.first_name(),
                    second_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    user=user,
                    registration_number=f"UG/2025/{10000+i}",
                    gender=choice(['M', 'F']),
                    blood_group=choice(['A', 'B', 'AB', 'O']),
                    faculty="Science",
                    department_id=1,   # adjust if needed
                    session=session,
                    level_id=1
                )
            )

        Student.objects.bulk_create(students, batch_size=BATCH_SIZE)

        self.stdout.write(f"{total} students created")

    # =========================
    # REGISTRATIONS (VERY FAST)
    # =========================
    def create_registrations(self):

        students = list(Student.objects.all())
        courses = list(Course.objects.all())
        session = Session.objects.first()

        registrations = []

        for student in students:

            selected_courses = sample(courses, 5)

            for course in selected_courses:

                registrations.append(
                    Registration(
                        student=student,
                        course=course,
                        session=session,
                        status='approved'
                    )
                )

        Registration.objects.bulk_create(
            registrations,
            batch_size=BATCH_SIZE
        )

        self.stdout.write("Registrations created")

    # =========================
    # COMPLAINTS (FAST)
    # =========================
    def create_complaints(self, total):

        students = list(Student.objects.all())
        courses = list(Course.objects.all())
        session = Session.objects.first()

        complaints = []

        for _ in range(total):

            complaints.append(
                Complaint(
                    student=choice(students),
                    course=choice(courses),
                    complaint_type=choice(['RESULT','COURSE','SCHEDULE','LECTURER','OTHER']),
                    subject=fake.sentence(),
                    session=session,
                    description=fake.paragraph(),
                    priority=choice(['LOW','MEDIUM','HIGH','URGENT'])
                )
            )

        Complaint.objects.bulk_create(
            complaints,
            batch_size=BATCH_SIZE
        )

        self.stdout.write(f"{total} complaints created")
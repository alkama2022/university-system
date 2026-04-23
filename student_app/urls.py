
from django.urls import path
from . import views

app_name = 'student_app'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('student_complaint/', views.create_complaint, name='create_complaint'),
    path('student_propile/', views.student_propile, name='student_propile'),
    path('home/', views.home, name='home'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('student/', views.student_data, name='student'),
    path('courses/', views.courses, name='courses'),
    path('enrollement/', views.enrollment_view, name='enrollement'),
    path('show_student/', views.show_student, name='list'),
    path('student_details/<int:pk>/', views.student_details, name='details'),
    path('facylty/depertiment/<int:dept_id>',views.show_depertment,name='depertment'),
    path('dashboard/',views.dashboard,name='dashboard')
]


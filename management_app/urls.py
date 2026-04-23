from django.urls import path
from . import views
app_name = 'management_app'

urlpatterns = [
    path('',views.show_timetable_view,name='show_tible'),
    path('show_results',views.show_results,name='show_result')
   
]

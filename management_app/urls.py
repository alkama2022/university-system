from django.urls import path
from . import views
app_name = 'management_app'

urlpatterns = [
    path('',views.show_tible,name='show_tible')
]


from django.contrib import admin # type: ignore
from django.urls import path,include # type: ignore

from debug_toolbar.toolbar import debug_toolbar_urls

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('student_app.urls')),
    path('management/',include('management_app.urls'))
] + debug_toolbar_urls()

# School_Management/urls.py

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as acc_views
from accounts import exam_officer_views, app_manager_views

urlpatterns = [
    # Short login URLs (no prefix)
    path('login/', acc_views.student_login, name='student_login'),
    path('staff/', acc_views.staff_login, name='staff_login'),
    path('exam/', exam_officer_views.exam_officer_login, name='exam_officer_login'),
    path('manager/', app_manager_views.app_manager_login, name='app_manager_login'),

    path('api/accounts/', include('accounts.api_urls', namespace='accounts_api')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path("", include('core.urls', namespace='core')),
    # path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
]

# Serve static and media when web server (cPanel) doesn't have a place to configure them
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production: Django serves static/media if cPanel Setup Python App has no static path
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
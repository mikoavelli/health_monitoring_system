from django.contrib.auth.views import LogoutView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('health/', views.health_view, name='health'),
    path('movements/', views.movements_view, name='movements'),
    path('standups/', views.standups_view, name='standups'),
    path('steps/', views.steps_view, name='steps'),
    path('devices/', views.devices_view, name='devices'),
    path('devices/add/', views.add_device_view, name='add_device'),
    path('devices/sync/<int:device_id>/', views.sync_device, name='sync_device'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

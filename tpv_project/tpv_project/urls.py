from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tpv/', include('tpv_app.urls')),
    path('', lambda request: redirect('login')),  # Redirige a la vista de login
]
"""
URL configuration for instytution_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('accounts.urls')),
    path('courses/',include('courses.urls')),
    path('custom-admin/',include('custom_admin.urls')),
    path('payments/',include('payments.urls')),
    path('course-admin/',include('course_admin.urls')),
    path('instructor/',include('instructor.urls')),
    path('shop-admin/',include('shop_admin.urls')),
    path('store/',include('store.urls')),
    path('order/',include('order.urls')),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns +=   path('__debug__/', include('debug_toolbar.urls')),
"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),

    path('api/auth/', include('dj_rest_auth.urls')),  # Login, logout, password reset, etc.
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # Registration endpoints

    # path("accounts/", include("allauth.urls")),  # Commented out to avoid conflicts
    
    path('api/', include('store.urls')),
    path('api/', include('product.urls')),
    path('api/', include('cart.urls')),
    path('api/', include('order.urls')),
    path('api/', include('address.urls')),
    path('api/', include('inventory.urls')),
    path('api/', include('report.urls')),
    path('api/', include('wishlist.urls')),

    path('api/', include('notification.urls')),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
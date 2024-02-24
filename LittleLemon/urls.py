from django.contrib import admin 
from django.urls import path, include 
  
urlpatterns = [ 
    path('admin/', admin.site.urls), 
    path('api/',include('LittleLemonAPI.urls')), 
    path('api/', include('djoser.urls')), 
    path('', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls')),
] 

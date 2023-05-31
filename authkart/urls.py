from django.urls import path
from authkart import views


urlpatterns = [
    path('login/', views.handlelogin, name='handlelogin'),
    path('logout/', views.handlelogout, name='handlelogout'),
    path('signup/', views.signup, name='signup'),
    path('auth/activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
]

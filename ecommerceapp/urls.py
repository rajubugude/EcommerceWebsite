from django.urls import path
from ecommerceapp import views
from .views import *


urlpatterns = [
    path('', views.index,name="index"),
    path('contact',views.contact, name="contact"),
    path('about',views.about, name="about"),
    path('profile/',views.profile, name="profile"),
    path('checkout/', views.checkout, name="checkout"),
    path('handle_payment/', views.handle_payment, name='handle_payment'),
    path('payment_failure/', views.payment_failure, name='payment_failure'),
    # path('payment_success/', views.payment_success, name='payment_success'),
]

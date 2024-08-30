from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_firstHTML, name="home"),
    path('cart/', views.Cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    path('hotel', views.hotel, name="hotel"),
    path('updateItem/', views.updateItem, name="updateItem"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('search/', views.search, name="search"),
]
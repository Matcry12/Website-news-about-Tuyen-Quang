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
]
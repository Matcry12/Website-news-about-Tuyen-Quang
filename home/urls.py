from django.contrib import admin
from django.urls import include, path
from .views import views

from .views.views import AddRoomView, AddHotelView, AddAccountView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news', views.news, name="news"),
    path('cart/', views.Cart, name="cart"),
    path('manage-account/', views.manage_account, name="manage_account"),
    path('', views.home, name="home"),
    path('updateItem/', views.updateItem, name="updateItem"),
    path('update_order/', views.updateOrder, name="update_order"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('detail/', views.detail, name="detail"),
    path('newdetail/', views.newdetail, name="newdetail"),
    path('profile/', views.profile, name="profile"),
    path('booking/', views.booking, name="booking"),
    path('completebooking/', views.completebooking, name='completebooking'),
    path('update-room/<room_id>', views.updateRoom, name="update_room"),
    path('update-hotel/<hotel_id>', views.updateHotel, name="update_hotel"),
    path('edit-profile/<user_id>', views.edit_profile, name="edit_profile"),
    path('add-room/', AddRoomView.as_view(), name="add_room"),
    path('add-hotel/', AddHotelView.as_view(), name="add_hotel"),
    path('add-account/', AddAccountView.as_view(), name="add_account"),
    path('delete-order/<order_id>/', views.delete_order, name='delete_order'),
    path('delete-hotel/<hotel_id>/', views.delete_hotel, name='delete_hotel'),
    path('delete-room/<room_id>/', views.delete_room, name='delete_room'),
    path('delete-account/<user_id>/', views.delete_account, name='delete_account'),
    path('return-room/<order_id>/', views.return_room, name='return_room'),
    path('history-list/', views.historylist, name='historylist'),
    path('export-history/', views.export_history, name='export_history'),
    path('export-accounts/', views.export_account, name='export_account'),
    path('export-hotel/', views.export_hotel, name='export_hotel'),
    path('download_example_hotel/', views.generate_example_hotel, name='download_example_hotel'),
    path('download_example_room/', views.generate_example_room, name='download_example_room'),
    path('create-superuser/', views.create_superuser, name='create_superuser'),
]
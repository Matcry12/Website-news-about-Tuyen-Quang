from .views import *

def delete_order(request, order_id):

    storage = get_messages(request)
    for message in storage:
        pass  # Iterating through storage clears it

    user_profile = UserProfile.objects.get(user=request.user)
    
    orderD = order.objects.get(id=order_id)
    if orderD.room.product.owner != request.user and orderD.customer != request.user:
        return redirect('order')
    status_instance = StatusType.objects.get(name="Trống")
    orderD.room.status = status_instance
    orderD.room.save()
    orderD.delete()
    messages.success(request, "Order deleted successfully")
    return redirect('order')

def delete_room(request, room_id):
    storage = get_messages(request)
    for message in storage:
        pass  # Iterating through storage clears it

    user_profile = UserProfile.objects.get(user=request.user)
    
    room = Room.objects.get(id=room_id)
    if room.product.owner != request.user:
        return redirect('cart')
    room.delete()
    messages.success(request, "Room deleted successfully")
    return redirect('cart')

def delete_hotel(request, hotel_id):
    storage = get_messages(request)
    for message in storage:
        pass  # Iterating through storage clears it

    user_profile = UserProfile.objects.get(user=request.user)
    
    hotel = Product.objects.get(id=hotel_id)
    if hotel.owner != request.user and user_profile.role != 'admin':
        return redirect('cart')
    hotel.delete()
    messages.success(request, "Hotel deleted successfully")
    return redirect('cart')

def delete_account(request, user_id):
    storage = get_messages(request)
    for message in storage:
        pass  # Iterating through storage clears it
    user_profile = UserProfile.objects.get(user=request.user)
    
    user_profile_t = UserProfile.objects.get(user__id=user_id)
    user = User.objects.get(id = user_id)

    if user_profile.role != 'admin':
        return redirect('home')
    
    user_profile_t.delete()
    user.delete()
    messages.success(request, "User deleted successfully")
    return redirect('manage_account')
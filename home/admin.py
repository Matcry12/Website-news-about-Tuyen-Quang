from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Product)
admin.site.register(order)
admin.site.register(cart)
admin.site.register(new)
admin.site.register(category)
admin.site.register(UserProfile)
admin.site.register(Room)
admin.site.register(history)
admin.site.register(RoomType)
admin.site.register(ProductType)
admin.site.register(StatusType)
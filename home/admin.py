from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(customer)
admin.site.register(Product)
admin.site.register(order)
admin.site.register(cart)
admin.site.register(new)
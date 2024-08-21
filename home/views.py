from django.shortcuts import render
from django.http import HttpResponse
from .models import *

def get_firstHTML(request):
    news = new.objects.all()
    context = {'news': news}
    return render(request, 'apps/home.html', context)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        _order, created = order.objects.get_or_create(_customer = customer, complete = False)
        items = _order.cart_set.all()
    else:
        items =[]
        _order = {'getCartItems': 0, 'getTotalPrice': 0}
    products = product.objects.all()
    context = {'items': items, 'order': _order, 'products': products}
    return render(request, 'apps/cart.html', context)
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        _order, created = order.objects.get_or_create(_customer = customer, complete = False)
        items = _order.cart_set.all()
    else:
        items =[]
        _order = {'getCartItems': 0, 'getTotalPrice': 0}
    products = product.objects.all()
    context = {'items': items, 'order': _order, 'products': products}
    return render(request, 'apps/checkout.html', context)
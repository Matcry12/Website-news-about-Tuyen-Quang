from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
import json

def get_firstHTML(request):
    news = new.objects.all()
    context = {'news': news}
    return render(request, 'apps/home.html', context)
def Cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        _order, created = order.objects.get_or_create(_customer = customer, complete = False)
        items = _order.cart_set.all()
    else:
        items =[]
        _order = {'getCartItems': 0, 'getTotalPrice': 0}
    products = Product.objects.all()
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
    products = Product.objects.all()
    context = {'items': items, 'order': _order, 'products': products}
    return render(request, 'apps/checkout.html', context)
def hotel(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'apps/hotel.html', context)
def updateItem(request):
    data = json.loads(request.body)

    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id = productId)
    Order, created = order.objects.get_or_create(_customer = customer, complete = False)
    Cart, created = cart.objects.get_or_create(Order = Order, product = product)

    if Cart.quantity > 0:
        if action == 'add':
            Cart.quantity += 1
        elif action == 'remove':
            Cart.quantity -= 1
    else:
        Cart.delete()
    Cart.save()


    return JsonResponse('added', safe=False)
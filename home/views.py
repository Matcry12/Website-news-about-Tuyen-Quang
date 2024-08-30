from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

def get_firstHTML(request):
    news = new.objects.all()
    if request.user.is_authenticated:
        user_not_login = "none"
    else:
        user_not_login = "block"
    context = {'news': news, 'user_not_login': user_not_login}
    return render(request, 'apps/home.html', context)
def Cart(request):
    if request.user.is_authenticated:
        customer = request.user
        _order, created = order.objects.get_or_create(_customer = customer, complete = False)
        items = _order.cart_set.all()
    else:
        items =[]
        _order = {'getCartItems': 0, 'getTotalPrice': 0, 'getTotal': 0}
    if request.user.is_authenticated:
        user_not_login = "none"
    else:
        user_not_login = "block"
    products = Product.objects.all()
    context = {'items': items, 'order': _order, 'products': products, 'user_not_login': user_not_login}
    return render(request, 'apps/cart.html', context)
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        _order, created = order.objects.get_or_create(_customer = customer, complete = False)
        items = _order.cart_set.all()
    else:
        items =[]
        _order = {'getCartItems': 0, 'getTotalPrice': 0}
    if request.user.is_authenticated:
        user_not_login = "none"
    else:
        user_not_login = "block"
    products = Product.objects.all()
    context = {'items': items, 'order': _order, 'products': products, 'user_not_login': user_not_login}
    return render(request, 'apps/checkout.html', context)
def hotel(request):
    products = Product.objects.all()
    if request.user.is_authenticated:
        user_not_login = "none"
    else:
        user_not_login = "block"
    context = {'products': products, 'user_not_login': user_not_login}
    return render(request, 'apps/hotel.html', context)
def updateItem(request):
    data = json.loads(request.body)

    productId = data['productId']
    action = data['action']

    customer = request.user
    product = Product.objects.get(id = productId)
    Order, created = order.objects.get_or_create(_customer = customer, complete = False)
    Cart, created = cart.objects.get_or_create(Order = Order, product = product)

    if Cart.quantity > 0 or action == 'add':
        if action == 'add':
            Cart.quantity += 1
        elif action == 'remove':
            Cart.quantity -= 1
    else:
        Cart.delete()
    Cart.save()

    return JsonResponse('added', safe=False)

def register(request):
    form = CreationUserForm()
    context = {'form': form}
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = CreationUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else: messages.info(request, 'Đăng ký không phù hợp!')

    return render(request, 'apps/register.html', context)
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else: messages.info(request, 'Tài khoản hoặc mật khẩu không đúng!')

    context = {}
    return render(request, 'apps/login.html', context)
def logoutPage(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render
from .models import Product  # Adjust the import based on your project structure

def search(request):
    # Determine if the user is logged in or not
    user_not_login = "none" if request.user.is_authenticated else "block"

    # Initialize context with default values
    context = {
        'user_not_login': user_not_login,
        'searched': '',  # Default value for search term
        'keys': []  # Default empty list for search results
    }

    # Check if the request method is POST
    if request.method == "POST":
        # Get the search term from POST data
        searched = request.POST.get("searched", "")
        # Update context with the search term and results
        context['searched'] = searched
        context['keys'] = Product.objects.filter(name__icontains=searched)  # Use icontains for case-insensitive search

    return render(request, 'apps/search.html', context)

    
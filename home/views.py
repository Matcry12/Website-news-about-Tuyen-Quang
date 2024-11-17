from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import *
from django.db.models import Q
import json
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.db.models.functions import Cast
from django.template.loader import render_to_string
from django.utils import timezone

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
        user_profile = UserProfile.objects.get(user=customer)
        # Corrected the field name to `customer`
        order_instance = order.objects.filter(customer=customer)
        user_not_login = "none"
    else:
        order_instance = {}  # If the user is not authenticated, we don't need to query orders
        user_not_login = "block"
        user_profile = None

    context = {
        'user_not_login': user_not_login,
        'order_instance': order_instance,  # Add the orders to the context for use in the template
        'profile': user_profile
    }

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
    # Start with all products
    products = Product.objects.all()
    
    # Handle the search query from GET request
    query = request.GET.get('q', '')
    if query:
        products = products.filter(name__icontains=query)
        # If a search is made, clear selected categories (optional, based on your requirement)
        selected_categories = []
    else:
        # If no search, use selected categories from session
        selected_categories = request.session.get('selected_categories', [])

    # Handle selected categories from POST request
    if request.method == 'POST':
        selected_categories = request.POST.getlist('category')
        # Store the selected categories in the session
        request.session['selected_categories'] = selected_categories

        if selected_categories:
            # Filter products that have all the selected categories
            for item in selected_categories:
                products = products.filter(categories__name=item)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_html = render_to_string('partials/product_list.html', {'products': products}, request)
        return JsonResponse({'products_html': products_html})


    # Load all categories for the checkbox list
    categories = category.objects.all()  # Ensure the model name is correct

    # Check if the user is authenticated
    user_not_login = "none" if request.user.is_authenticated else "block"

    context = {
        'products': products,
        'categories': categories,
        'selected_categories': selected_categories,  # Pass selected categories to the template
        'user_not_login': user_not_login
    }

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
# views.py

def detail(request):
    user_not_login = "none" if request.user.is_authenticated else "block"
    id = request.GET.get('id', '')
    product = get_object_or_404(Product, id=id)
    rooms_on_sale = product.rooms.filter(status=True)

    # Set default sorting order
    price_order = 'price_numeric'

    if request.method == 'POST':
        # Get the selected sorting option from the POST data
        price_sort = request.POST.get('priceSort')
        if price_sort == 'desc':
            price_order = '-price_numeric'  # Sort High to Low
        elif price_sort == 'asc':
            price_order = 'price_numeric'   # Sort Low to High

    # Create an annotation to convert `price` to an integer for sorting, assuming prices are in format like "1.000"
    rooms_on_sale = rooms_on_sale.annotate(
        price_numeric=Cast(Cast('price', IntegerField()), IntegerField())
    ).order_by(
        Case(When(status=True, then=0), When(status=False, then=1)),
        price_order
    )

    context = {
        'product': product,
        'user_not_login': user_not_login,
        'rooms': rooms_on_sale
    }
    return render(request, 'apps/detail.html', context)


def news(request):
    if request.user.is_authenticated:
        user_not_login = "none"
    else:
        user_not_login = "block"
    id = request.GET.get('id', '')
    news = new.objects.filter(id = id)
    context = {'news': news, 'user_not_login': user_not_login}
    return render(request, 'apps/news.html', context)

def profile(request):
    if request.user.is_authenticated:
        user_not_login = "none"
        user_profile = UserProfile.objects.get(user=request.user)
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        user_profile = None  # No profile available for non-logged-in users
    context = {'profile': user_profile, 'user_not_login': user_not_login}
    
    return render(request, 'apps/profile.html', context)

def booking(request, order_id=None):
    # Get the product_id and room_id from query parameters
    product_id = request.GET.get('product_id')
    room_id = request.GET.get('room_id')

    # Handle user login status
    user_not_login = "none" if request.user.is_authenticated else "block"

    # If product_id and room_id are provided, fetch corresponding objects
    if product_id and room_id:
        product = get_object_or_404(Product, id=product_id)
        room = get_object_or_404(Room, id=room_id, product=product)
    else:
        product = room = None

    # If order_id is provided, fetch the existing order
    if order_id:
        order_obj = get_object_or_404(order, id=order_id)
    else:
        order_obj = None

    if request.method == 'POST':
        # Extract form data
        customer_name = request.POST.get('customer_name')
        cccd = request.POST.get('cccd')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        booking_date = request.POST.get('booking_date')
        payment_method = request.POST.get('payment_method')

        # Ensure room_id is included
        room_id = request.POST.get('room_id')

        # Form validation (optional)
        if not all([customer_name, cccd, address, phone_number, booking_date, room_id]):
            return HttpResponse("All fields are required.", status=400)

        # Handle order creation or update
        if order_obj:
            # Update existing order
            order_obj.cname = customer_name
            order_obj.address = address
            order_obj.phonecall = phone_number
            order_obj.datebook = timezone.datetime.strptime(booking_date, "%Y-%m-%d")
            order_obj.room = get_object_or_404(Room, id=room_id)
            order_obj.save()
        else:
            # Create a new order
            order_obj = order.objects.create(
                customer=request.user,
                cname=customer_name,
                address=address,
                phonecall=phone_number,
                datebook=timezone.datetime.strptime(booking_date, "%Y-%m-%d"),
                complete=False,  # Order is incomplete initially
                room=get_object_or_404(Room, id=room_id)
            )

        # Handle cart items (add the room to the cart)
        room = get_object_or_404(Room, id=room_id)  # Get the room based on the provided room_id
        cart_item = cart.objects.create(
            order=order_obj,
            room=room,
            quantity=1,
        )
        messages.success(request, "Bạn đã đặt phòng thành công")
    if order_obj:
        room_obj = order_obj.room  # Get the room associated with the order
    else:
        room_obj = room  # Use the room from query parameters if available

    # Context to pass to the template
    context = {
        'order': order_obj,
        'room': room_obj,
        'product': product,
        'user_not_login': user_not_login,
    }

    return render(request, 'apps/booking.html', context)
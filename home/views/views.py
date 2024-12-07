from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from ..models import *
from django.db.models import Q
import json
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.db.models.functions import Cast
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.paginator import Paginator
from home.templatetags.forms import RoomForm, RoomPicForm, ProductForm, ProductPicForm, RoomFormCreate, ProductFormCreate, SuperUserForm, UserEditForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from openpyxl.styles import Border, Side, Font
from django.db.models import Q, Value, F
from django.db.models.functions import Concat
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
import openpyxl

from django.views.generic import TemplateView

from .history_view import *
from .add_view import *
from .entrance_view import *
from .manage_hotel import *
from .delete_view import *
from .export_view import *
from .generate_view import *


def news(request):
    news = new.objects.all()
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user = request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None
    context = {'news': news, 'user_not_login': user_not_login, 'profile': profile}
    return render(request, 'apps/news.html', context)

def home(request):
    # Start with all products
    products = Product.objects.all()
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user = request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None
    
    # Handle the search query from GET request
    query = request.GET.get('q', '')
    if query:
        products = products.filter(name__icontains=query)
        selected_categories = []  # Optional: Clear other filters if a search is performed
        selected_product_types = []
        selected_room_types = []
    else:
        # Retrieve filters from session if no search
        selected_categories = request.session.get('selected_categories', [])
        selected_product_types = request.session.get('selected_product_types', [])
        selected_room_types = request.session.get('selected_room_types', [])

    # Handle selected categories from POST request
    if request.method == 'POST':
        selected_categories = request.POST.getlist('category')
        selected_product_types = request.POST.getlist('product_type')
        selected_room_types = request.POST.getlist('room_type')
        # Store the selected categories in the session
        request.session['selected_categories'] = selected_categories
        request.session['selected_product_types'] = selected_product_types
        request.session['selected_room_types'] = selected_room_types

        if selected_categories:
            # Filter products that have all the selected categories
            for item in selected_categories:
                products = products.filter(categories__name=item)
        if selected_product_types:
            # Filter products that have all the selected categories
            for item in selected_product_types:
                products = products.filter(product_type__name=item)
        if selected_room_types:
            # Filter products that have all the selected categories
            for item in selected_room_types:
                products = products.filter(room_types__name=item)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_html = render_to_string('partials/product_list.html', {'products': products}, request)
        return JsonResponse({'products_html': products_html})


    # Load all categories for the checkbox list
    categories = category.objects.all()  # Ensure the model name is correct
    product_types = ProductType.objects.all()  # Ensure the model name is correct
    room_types = RoomType.objects.all()  # Ensure the model name is correct
    # Check if the user is authenticated

    context = {
        'products': products,
        'categories': categories,
        'product_types': product_types,
        'room_types': room_types,
        'profile': profile,
        'selected_categories': selected_categories,
        'selected_product_types': selected_product_types,
        'selected_room_types': selected_room_types,
        'user_not_login': user_not_login,
    }
    return render(request, 'apps/home.html', context)

# views.py

def detail(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user = request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None
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
        'rooms': rooms_on_sale,
        'profile': profile
    }
    return render(request, 'apps/detail.html', context)


def newdetail(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user = request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None
    id = request.GET.get('id', '')
    news = new.objects.filter(id = id)
    context = {'news': news, 'user_not_login': user_not_login, 'profile': profile}
    return render(request, 'apps/newdetail.html', context)

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
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user = request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None

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
            order_obj.cccd = cccd
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
                cccd = cccd,
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
        return redirect('completebooking')

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
        'profile': profile
    }

    return render(request, 'apps/booking.html', context)

def updateRoom(request, room_id):
    if request.user.is_authenticated:
        user_not_login = "none"
        user_profile = UserProfile.objects.get(user=request.user)
        room =  Room.objects.get(id = room_id)
        if room.product.owner != user_profile.user:  # Compare the actual User object
            return redirect('home') 
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        user_profile = None  # No profile available for non-logged-in users
        return redirect('login')
    room_form = RoomForm(request.POST or None, request.FILES or None , instance=room)
    pic_form = RoomPicForm(request.POST or None , request.FILES or None , instance=room)
    if room_form.is_valid() and pic_form.is_valid():
            room_form.save()
            pic_form.save()

            return redirect('cart')  # Redirect to room details page after saving
    context = {'profile': user_profile, 'user_not_login': user_not_login, 'room': room, 'room_form': room_form, 'pic_form': pic_form}
    return render(request, 'apps/update_room.html', context)

def updateHotel(request, hotel_id):
    if request.user.is_authenticated:
        user_not_login = "none"
        user_profile = UserProfile.objects.get(user=request.user)
        hotel =  Product.objects.get(id = hotel_id)
        if hotel.owner != user_profile.user:  # Compare the actual User object
            return redirect('home') 
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        user_profile = None  # No profile available for non-logged-in users
        return redirect('login')
    hotel_form = ProductForm(request.POST or None, request.FILES or None , instance=hotel)
    pic_form = ProductPicForm(request.POST or None , request.FILES or None , instance=hotel)
    if hotel_form.is_valid() and pic_form.is_valid():
            hotel_form.save()
            pic_form.save()

            return redirect('cart')  # Redirect to room details page after saving
    context = {'profile': user_profile, 'user_not_login': user_not_login, 'hotel': hotel, 'hotel_form': hotel_form, 'pic_form': pic_form}
    return render(request, 'apps/update_hotel.html', context)

@login_required
def edit_profile(request, user_id):
    if request.user.is_authenticated:
        user_not_login = "none"
        user_profile = UserProfile.objects.get(user=request.user)
    else:
        user_not_login = "block"
        user_profile = None  # No profile available for non-logged-in users
        return redirect('login')
    if user_profile.role != 'admin':
        user_form = UserEditForm(request.POST or None, instance=request.user)
        profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
    else:
        user_profile_t = UserProfile.objects.get(user__id=user_id)
        user = User.objects.get(id = user_id)
        user_form = UserEditForm(request.POST or None, instance=user)
        profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile_t)
    if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save User model changes
            profile_form.save()  # Save UserProfile model changes
            if user_profile.role != 'admin':
                return redirect('profile')  # Redirect after saving
            else:
                return redirect('manage_account')
    allow = False
    context = {'profile': user_profile, 'user_not_login': user_not_login, 'user_form': user_form, 'profile_form':profile_form, 'allow': allow}
    return render(request, 'apps/edit_profile.html', context)

def return_room(request, order_id):
    # Fetch the order
    orderD = order.objects.get(id=order_id)
    
    # Save the order details to the history table
    history.objects.create(
        customer=orderD.customer,
        dateOrder=orderD.dateOrder,
        datebook=orderD.datebook,
        address=orderD.address,
        cname=orderD.cname,
        cccd = orderD.cccd,
        phonecall=orderD.phonecall,
        room=orderD.room,
    )
    
    messages.success(request, "Order complete successfully")
    # Delete the order
    orderD.delete()
    
    # Redirect to the cart page
    return redirect('cart')

def filter_users(request, user_profile):
    users = UserProfile.objects.all()
    name = request.GET.get('name')
    if name:
        users = users.filter(user__username=name)

    cccd = request.GET.get('cccd')
    if cccd:
        users = users.filter(cccd=cccd)
    
    phone = request.GET.get('phonecall')
    if phone:
        users = users.filter(phonecall=phone)

    fullname = request.GET.get('fullname')
    if fullname:
        users = UserProfile.objects.annotate(
            full_name=Concat(F('user__last_name'), Value(' '), F('user__first_name'))
        ).filter(
            Q(full_name__icontains=fullname)
        )

    email = request.GET.get('email')
    if email:
        users = users.filter(user__email=email)

    if user_profile.role != 'admin':
        return None
    
    return users

def manage_account(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'admin':
            return redirect('home')
        user_not_login = "none"
        users = filter_users(request, user_profile)
        allowed = users.exists()
        count = users.count()
        paginator = Paginator(users, 10)  # Paginate results
        page_number = request.GET.get('page')
        users_page = paginator.get_page(page_number)
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        users_page = None
        return redirect('home')
    
    context = {'user_not_login': user_not_login, 'users_page': users_page, 'allowed': allowed, 'count': count, 'profile': user_profile}

    return render(request, 'apps/manage_account.html', context)


def create_superuser(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
    else:
        user_profile = None
    # Check if there are any superusers in the database
    if not User.objects.filter(is_superuser=True).exists():
        # If no superusers exist, allow any user to create a superuser
        if request.method == 'POST':
            form = SuperUserForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')  # Redirect to the admin page or another page
        else:
            form = SuperUserForm()

        return render(request, 'apps/create_superuser.html', {'form': form})

    # If there are superusers, ensure the user is authenticated and is a superuser
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('home')  # Redirect to home page if the user is not authenticated or not a superuser

    # Allow superusers to create another superuser
    if request.method == 'POST':
        form = SuperUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the admin page or another page
    else:
        form = SuperUserForm()

    return render(request, 'apps/create_superuser.html', {'form': form, 'profile': user_profile})


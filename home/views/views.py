from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.db import transaction
from django.urls import reverse
from ..models import *
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Value, F, FloatField, Count, CharField, Avg, BooleanField
import json
from collections import defaultdict
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.db.models.functions import Cast, Substr, StrIndex, Concat
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.paginator import Paginator
from home.templatetags.forms import RoomForm, RoomPicForm, ProductForm, ProductPicForm, RoomFormCreate, ProductFormCreate, UserProfileFormUser , SuperUserForm, UserEditForm, UserProfileForm, OrderForm, UserPasswordForm, ProductFormCreateUser
from django.contrib.auth.decorators import login_required
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from openpyxl.styles import Border, Side, Font
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
import openpyxl
from django.contrib.messages import get_messages
from datetime import datetime
from django.core.mail import send_mail
from django.views.generic import TemplateView, CreateView
from django.http import QueryDict
from io import BytesIO
from django.core.serializers import serialize
from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate, gettext
from .history_view import *
from .add_view import *
from .entrance_view import *
from .manage_hotel import *
from .delete_view import *
from .export_view import *
from .generate_view import *

def error_login(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user = request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None

    context = {'user_not_login': user_not_login, 'profile': profile}

    return render(request, 'apps/errorlogin.html', context)

def reset_password(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user = request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None

    context = {'user_not_login': user_not_login, 'profile': profile}

    return render(request, 'apps/reset_password.html', context)

def news(request):
    news = new.objects.all()
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user = request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None
    context = {'news': news, 'user_not_login': user_not_login, 'profile': profile, 'page_name': 'news', 'home': "home",}
    return render(request, 'apps/news.html', context)

def parse_amount_start(product):
    # Extract and convert amount_start to a numeric value
    amount_start = product.amountprice.split('-')[0]
    return float(amount_start.replace(',', '').replace('.', ''))

def parse_price(price):
    try:
        return int(price.replace('.', '').strip())  # Remove dots and whitespace, then convert
    except (ValueError, AttributeError):
        return 0  # Default to 0 if parsing fails

def home(request):
    # Annotate amount_start for sorting
    products = Product.objects.annotate(
        comment_count=Count('comments'),
        average_rating=Avg('comments__rating')
    )

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        user_not_login = "none"
    else:
        profile = None
        user_not_login = "block"

    # Handle search query
    query = request.GET.get('q', '')
    if query:
        products = products.filter(name__icontains=query)
        selected_categories = []
        selected_product_types = []
        selected_room_types = []
    else:
        selected_categories = request.session.get('selected_categories', [])
        selected_product_types = request.session.get('selected_product_types', [])
        selected_room_types = request.session.get('selected_room_types', [])

    # Handle filters from POST request
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        selected_categories = request.POST.getlist('category')
        selected_product_types = request.POST.getlist('product_type')
        selected_room_types = request.POST.getlist('room_type')
        rate = request.POST.get('rate', 'all')
        max_price = request.POST.get('max_price')
        min_price = request.POST.get('min_price')

        # Store selections in session
        request.session.update({
            'selected_categories': selected_categories,
            'selected_product_types': selected_product_types,
            'selected_room_types': selected_room_types,
            'name': name,
            'max_price': max_price,
            'min_price': min_price,
            'rate': rate,
        })

        # Apply filters
        if name:
            products = products.filter(name__icontains=name)
        if selected_categories:
            products = products.filter(categories__name__in=selected_categories).distinct()
        if selected_product_types:
            products = products.filter(product_type__name__in=selected_product_types).distinct()
        if selected_room_types:
            products = products.filter(room_types__name__in=selected_room_types).distinct()

        # Price filtering
        start_price = min_price
        end_price = max_price

        if start_price or end_price:  # Check if either price is provided
            filtered_products = []

            for item in products:
                try:
                    
                    prices = item.amountprice.split('-')
                    amount_start = parse_price(prices[0])
                    
                    if amount_start <= int(end_price) and amount_start >= int(start_price):
                        filtered_products.append(item)
                        
                except (ValueError, IndexError):
                    # Handle cases where amountprice is invalid
                    continue

            # Apply filtering once
            filtered_ids = list({product.id for product in filtered_products})
            products = products.filter(id__in=filtered_ids)

        # Rate filtering
        if rate and rate != 'all':
            try:
                rate = int(rate)
                products = products.filter(rate__gte=rate)
            except ValueError:
                pass

    # Load filters for the template
    categories = category.objects.all()
    product_types = ProductType.objects.all()
    room_types = RoomType.objects.all()

    sorted_products = sorted(products, key=parse_amount_start)

    status_id = StatusType.objects.filter(name='Trống/Empty').values_list('id', flat=True).first()
    product_rooms = {}
    if status_id:
        product_rooms = {
            product.id: product.rooms.filter(status_id=status_id)
            for product in products
        }
    else:
        product_rooms = {}
        print("Status 'Trống' not found.")

    context = {
        'products': sorted_products,
        'categories': categories,
        'product_types': product_types,
        'room_types': room_types,
        'profile': profile,
        'product_rooms': product_rooms,
        'selected_categories': selected_categories,
        'selected_product_types': selected_product_types,
        'selected_room_types': selected_room_types,
        'user_not_login': user_not_login,
        'home': "home",
    }
    return render(request, 'apps/home.html', context)

# views.py
def detail(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        user_not_login = "none"
    else:
        user_not_login = "block"
        profile = None

    id = request.GET.get('id', '')
    product = get_object_or_404(Product, id=id)
    status = StatusType.objects.get(name='Trống/Empty')
    rooms_on_sale = product.rooms.filter(status=status)
    comments = Comment.objects.filter(product=product).order_by('-created_at')
    paginator_comment = Paginator(comments, 5)
    page_number_comment = request.GET.get('comment_page')
    comments_page = paginator_comment.get_page(page_number_comment)

    # Get sorting parameter from GET
    price_sort = request.GET.get('priceSort', 'asc')
    price_order = 'price_numeric' if price_sort == 'asc' else '-price_numeric'

    # Annotate and order rooms
    rooms_on_sale = rooms_on_sale.annotate(
        price_numeric=Cast(Cast('price', IntegerField()), IntegerField())
    ).order_by(
        Case(When(status=True, then=0), When(status=False, then=1)),  # Sort by status
        price_order
    )

    # Pagination
    paginator = Paginator(rooms_on_sale, 5)
    page_number = request.GET.get('page')
    room_page = paginator.get_page(page_number)

    # Generate query string for pagination links
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_params.pop('comment_page', None) 
    query_string = query_params.urlencode()

    if request.method == 'POST':
        if profile == None:
            return redirect('error_login')
        rating = request.POST.get('rating')
        text = request.POST.get('comment')
        Comment.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            text=text
        )
        return HttpResponseRedirect(f"{reverse('detail')}?id={id}")
    
    context = {
        'product': product,
        'user_not_login': user_not_login,
        'rooms': room_page,
        'profile': profile,
        'room_page': room_page,
        'query_string': query_string,
        'comments': comments,
        'comments_page': comments_page,
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
        return redirect('reset_password')
    context = {'profile': user_profile, 'user_not_login': user_not_login}
    
    return render(request, 'apps/profile.html', context)

def booking(request, order_id=None):
    storage = get_messages(request)
    for message in storage:
        pass  # Iterating through storage clears it
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
        return redirect('error_login')
    
    error = ''

    # If product_id and room_id are provided, fetch corresponding objects
    if product_id and room_id:
        product = get_object_or_404(Product, id=product_id)
        room = get_object_or_404(Room, id=room_id, product=product)
    else:
        product = room = None
    
    outstock = StatusType.objects.filter(name='Đang được sử dụng/ In use').values_list('id', flat=True).first()
    wait = StatusType.objects.filter(name='Chờ/Wait').values_list('id', flat=True).first()

    if room.status.id == wait or room.status.id == outstock:
        return redirect('home')
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

        cbooking_date = datetime.strptime(booking_date, "%d/%m/%Y").date()
        current_date = now().date()
        

        if cbooking_date < current_date:
            error = 'Không thể đặt phòng trong quá khứ.'
        else:
            payment_method = request.POST.get('payment_method')
            # Ensure room_id is included
            room_id = request.POST.get('room_id')

            booking_date_obj = datetime.strptime(booking_date, "%d/%m/%Y")

            # Form validation (optional)
            if not all([customer_name, cccd, address, phone_number, booking_date_obj, room_id]):
                return HttpResponse("Xảy ra sự cố lỗi trong quá trình nhập thông tin. Vui lòng kiểm tra lại", status=400)

            if profile.role != 'customer':
                return HttpResponse("Tài khoản này không thể đặt phòng", status=400)

            # Handle order creation or update
            if order_obj:
                # Update existing order
                order_obj.cname = customer_name
                order_obj.address = address
                order_obj.cccd = cccd
                order_obj.phonecall = phone_number
                order_obj.datebook = booking_date_obj
                order_obj.room = get_object_or_404(Room, id=room_id)
                order_obj.method = payment_method
                order_obj.save()
            else:
                # Create a new order
                order_obj = order.objects.create(
                    customer=request.user,
                    cname=customer_name,
                    address=address,
                    phonecall=phone_number,
                    cccd = cccd,
                    datebook=booking_date_obj,
                    complete=False,  # Order is incomplete initially
                    method = payment_method,
                    room=get_object_or_404(Room, id=room_id)
                )

            # Handle cart items (add the room to the cart)
            room = get_object_or_404(Room, id=room_id)  # Get the room based on the provided room_id
            cart_item = cart.objects.create(
                order=order_obj,
                room=room,
                quantity=1,
            )
            status_instance = StatusType.objects.get(name="Chờ/Wait")
            room.status = status_instance
            room.save()
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
        'profile': profile,
        'error': error,
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
    error = ''
    room_form = RoomForm(request.POST or None, request.FILES or None , instance=room)
    pic_form = RoomPicForm(request.POST or None , request.FILES or None , instance=room)
    if room_form.is_valid() and pic_form.is_valid():
            room_form.save()
            pic_form.save()

            return redirect('cart')  # Redirect to room details page after saving
    elif request.method == 'POST': 
        error = 'Xảy ra lỗi trong quá trình nhập dữ liệu'
    context = {'profile': user_profile, 'user_not_login': user_not_login, 'room': room, 'room_form': room_form, 'pic_form': pic_form, 'error': error}
    return render(request, 'apps/update_room.html', context)

def updateHotel(request, hotel_id):
    if request.user.is_authenticated:
        user_not_login = "none"
        user_profile = UserProfile.objects.get(user=request.user)
        hotel =  Product.objects.get(id = hotel_id)
        if hotel.owner != user_profile.user and user_profile.role != 'admin':  # Compare the actual User object
            return redirect('home') 
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        user_profile = None  # No profile available for non-logged-in users
        return redirect('login')
    error = ''
    hotel_form = ProductForm(request.POST or None, request.FILES or None , instance=hotel)
    pic_form = ProductPicForm(request.POST or None , request.FILES or None , instance=hotel)
    if hotel_form.is_valid() and pic_form.is_valid():
            hotel_form.save()
            pic_form.save()

            return redirect('cart')  # Redirect to room details page after saving
    elif request.method == 'POST': 
        error = 'Xảy ra lỗi trong quá trình nhập dữ liệu'
    context = {'profile': user_profile, 'user_not_login': user_not_login, 'hotel': hotel, 'hotel_form': hotel_form, 'pic_form': pic_form, 'error': error}
    return render(request, 'apps/update_hotel.html', context)

def updateTrade(request, order_id):
    if request.user.is_authenticated:
        user_not_login = "none"
        user_profile = UserProfile.objects.get(user=request.user)
        Order =  order.objects.get(id = order_id)
        product_room = order.objects.get(id = order_id)
        if Order.room.product.owner != user_profile.user and Order.customer != user_profile.user:  # Compare the actual User object
            return redirect('home') 
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        user_profile = None  # No profile available for non-logged-in users
        return redirect('login')
    error = ''
    order_form = OrderForm(request.POST or None, request.FILES or None , instance=Order)
    if order_form.is_valid():
        # Check if the selected room belongs to the same product
        selected_room = order_form.cleaned_data['room']
        if selected_room.product != product_room.room.product and Order.customer != user_profile.user:
            error = 'Phòng được chọn không hợp lệ'
        else:
            # Save the form if validation passes
            order_form.save()
            return redirect('order')  # Redirect after successful update
    elif request.method == 'POST': 
        error = 'Xảy ra lỗi trong quá trình nhập dữ liệu'    
    
    context = {'profile': user_profile, 'user_not_login': user_not_login, 'order': Order, 'order_form': order_form, 'error': error}
    return render(request, 'apps/update_order.html', context)

@login_required
def edit_profile(request, user_id=None):
    # Check if the logged-in user is admin
    if request.user.is_authenticated:
        user_not_login = "none"
        user_profile = UserProfile.objects.get(user=request.user)  # The current user's profile
    else:
        user_not_login = "block"
        user_profile = None
        return redirect('login')
    
    # Handle user profile editing based on role
    if user_profile.role != 'admin':
        user_form = UserEditForm(request.POST or None,  request.FILES or None, instance=request.user)
        user_profile.base_password = None
        profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
    else:
        try:
            user_profile_t = UserProfile.objects.get(user__id=user_id) 
            user = User.objects.get(id=user_id)

            # Forms for the admin to edit another user
            user_form = UserEditForm(request.POST or None, request.FILES or None, instance=user)
            profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile_t)

            # Update base_password
            user_profile_t.base_password = None
        except UserProfile.DoesNotExist or User.DoesNotExist:
            messages.error(request, "Tài khoản không tồn tại")
            if user_profile.role != 'admin':
                return redirect('profile')
            else:
                return redirect('manage_account')
    # Save forms if valid and redirect accordingly
    error = ""
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "Cập nhật":
            if user_form.is_valid() and profile_form.is_valid():
                password1 = user_form.cleaned_data.get('password1')
                password2 = user_form.cleaned_data.get('password2')

                if password1 == password2:
                    user_form.save()
                    if user_profile:
                        user_profile.save()
                    elif user_profile_t:
                        user_profile_t.save()

                    profile_form.save()
                    
                    if user_profile.role != 'admin':
                        return redirect('profile')
                    else:
                        return redirect('manage_account')
                else:
                    error = 'Lỗi trong quá trình nhập dữ liệu'
            else:
                error = 'Lỗi trong quá trình nhập dữ liệu'
    # Default context
    context = {
        'profile': user_profile,
        'user_not_login': user_not_login,
        'user_form': user_form,
        'profile_form': profile_form,
        'error': error
    }
    
    return render(request, 'apps/edit_profile.html', context)

@login_required
def change_password(request, user_id=None):
    # Check if the logged-in user is authenticated
    if request.user.is_authenticated:
        user_not_login = "none"
        user_profile = get_object_or_404(UserProfile, user=request.user)
    else:
        return redirect('login')

    # Initialize password form outside of the conditional block
    password_form = UserPasswordForm(request.POST or None, request.FILES or None, instance=request.user)
    error = ""

    # Handle role-specific logic
    if user_profile.role != 'admin':
        user_profile.base_password = None

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "Cập nhật":
            if password_form.is_valid():
                password1 = password_form.cleaned_data.get('password1')
                password2 = password_form.cleaned_data.get('password2')

                if password1 == password2:
                    password_form.save()
                    if user_profile:
                        user_profile.save()

                    return redirect('profile')
                else:
                    error = 'Lỗi: Mật khẩu không khớp'
            else:
                error = 'Lỗi: Vui lòng kiểm tra lại dữ liệu nhập'

    # Default context
    context = {
        'profile': user_profile,
        'user_not_login': user_not_login,
        'password_form': password_form,
        'error': error
    }
    
    return render(request, 'apps/change_password.html', context)

def return_room(request, order_id):

    storage = get_messages(request)
    for message in storage:
        pass  # Iterating through storage clears it

    # Fetch the order
    
    orderD = order.objects.get(id=order_id)

    order_date = orderD.datebook.date() if hasattr(orderD.datebook, 'date') else orderD.datebook
    current_date = now().date()

    if order_date <= current_date:
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
            method = orderD.method,
        )
        
        messages.success(request, "Order complete successfully")

        status_instance = StatusType.objects.get(name="Trống/Empty")
        orderD.room.status = status_instance
        orderD.room.save()
        # Delete the order
        orderD.delete()
    
    # Redirect to the cart page
    return redirect('order')

def filter_users(request, user_profile):
    users = UserProfile.objects.all()

    name = request.GET.get('name')
    if name:
        users = users.filter(user__username__icontains=name) 

    hotel = request.GET.get('hotel')

    if hotel:
        users = users.filter(user__products__name__icontains=hotel).distinct()

    cccd = request.GET.get('cccd')
    if cccd:
        users = users.filter(cccd__icontains=cccd)
    
    phone = request.GET.get('phonecall')
    if phone:
        users = users.filter(phonecall__icontains=phone)

    fullname = request.GET.get('fullname')
    if fullname:
        users = users.annotate(
            full_name=Concat(F('user__last_name'), Value(' '), F('user__first_name'))
        ).filter(
            full_name__icontains=fullname 
        )

    email = request.GET.get('email')
    if email:
        users = users.filter(user__email__icontains=email) 
    
    role_ids = request.GET.getlist('role')
    if 'all' not in role_ids:
        if '1' in role_ids:
            users = users.filter(role='customer')
        if '2' in role_ids:
            users = users.filter(role='seller')
        if '3' in role_ids:
            users = users.filter(role='admin')
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
        paginator = Paginator(users, 10) 
        page_number = request.GET.get('page')
        users_page = paginator.get_page(page_number)

        error = ''

        query_params = request.GET.copy()
        query_params.pop('page', None)  
        query_string = query_params.urlencode() 

    else:
        user_not_login = "block"
        users_page = None
        return redirect('home')

    if request.method == 'POST':
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = json.loads(request.body)
            selected_users = data.get("users", [])
            action = data.get("action", "")
            if action == "reset-login":
                
                reset_results = []
                for user_id in selected_users:
                    user = User.objects.get(id=user_id)
                    profile = UserProfile.objects.get(user__id = user_id)
                    new_password = User.objects.make_random_password(length=10)
                    user.set_password(new_password)
                    profile.base_password = new_password
                    profile.save()
                    user.save()

                    try:
                        send_mail(
                            'Mật khẩu của bạn đã được làm mới',
                            f'Xin chào {user.username},\n\nMật khẩu mới của bạn là: {new_password}\n\nXin hãy đăng nhập và sửa nó sớm nhất có thể.',
                            'fdtywadw@gmail.com',  # From email
                            [user.email],  # To email
                            fail_silently=True  # Fail silently to avoid exceptions
                        )
                    except Exception as e:
                        print(f"Email failed to send: {e}")

                    reset_results.append({
                        "account": user.username,
                        "last_name": user.last_name,
                        "first_name": user.first_name,
                        "email": user.email,
                        "new_password": new_password,
                    })
                request.session["reset_results"] = reset_results
                return JsonResponse({'redirect_url': '/xuat-tai-khoan-mat-mau-moi/'}, status=200)
            if action == "delete-account":
                data = json.loads(request.body)
                selected_users = data.get("users", [])

                try:
                    deleted_count, _ = User.objects.filter(id__in=selected_users).delete()
                    return JsonResponse({"message": f"Đã xóa thành công!"}, status=200)
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=400)
            if action == "provide-role":
                data = json.loads(request.body)
                selected_users = data.get("users", [])

                try:
                    users = UserProfile.objects.filter(user__id__in=selected_users)
                    users.update(role='seller')
                    return JsonResponse({"message": f"Đã cấp vai trò thành công!"}, status=200)
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=400)
            if action == "reset-role":
                data = json.loads(request.body)
                selected_users = data.get("users", [])

                try:
                    users = UserProfile.objects.filter(user__id__in=selected_users)
                    users.update(role='customer')
                    return JsonResponse({"message": f"Đã loại bỏ vai trò thành công!"}, status=200)
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=400)
        if user_profile.role == 'admin' and 'account_excel' in request.FILES:
            excel_file = request.FILES['account_excel']
            
            # Open the uploaded Excel file
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active
                
                # Define the column headers for products
                headers = [
                    'Tên tài khoản (username)', 
                    'Email', 
                    'Tên riêng', 
                    'Tên đệm', 
                    'Số điện thoại',
                    'Mật khẩu',
                ]
                with transaction.atomic():
                    # Iterate over the rows in the sheet
                    for row in sheet.iter_rows(min_row=2, values_only=True):
                        account_data = dict(zip(headers, row))

                        username = account_data.get('Tên tài khoản (username)', '').strip()

                        # Check if the username is not empty
                        if not username:
                            continue  # Skip this row if username is missing or empty

                        # Check if the user already exists, if so, skip
                        try:
                            user = User.objects.get(username=username)
                        except ObjectDoesNotExist:
                            user = None  # If user does not exist, proceed with creating new user
                        
                        if not user:  # Only create a new user if it doesn't exist
                            # Create the new user and set password
                            user = User.objects.create_user(
                                username=username,
                                email=account_data['Email'],
                                first_name=account_data['Tên riêng'],
                                last_name=account_data['Tên đệm'],
                                password=account_data['Mật khẩu'],  # Set password using 'create_user'
                            )

                            # Create the user profile
                            UserProfile.objects.create(
                                user=user,
                                role = 'seller',
                                phonecall=account_data['Số điện thoại'],
                                base_password = account_data['Mật khẩu'],
                            )
            except Exception as e:
                error = 'Lỗi trong quá trình nhập dữ liệu'
    
    products = Product.objects.all()
    account_hotel = {
        product.id: product.owner
        for product in products
    }

    context = {'user_not_login': user_not_login,'error': error, 'products': products, 'users_page': users_page, 'allowed': allowed, 'count': count, 'profile': user_profile, 'query_string': query_string, 'account_hotel': account_hotel}

    return render(request, 'apps/manage_account.html', context)

def filter_rooms(request):
    rooms = Room.objects.all()

    name_ids = request.GET.get('name')
    if name_ids and 'all' not in name_ids:
        rooms = rooms.filter(product__id__in=name_ids).distinct()

    room_ids = request.GET.getlist('room_type')
    if room_ids and 'all' not in room_ids:
        rooms = rooms.filter(room_type__id__in=room_ids).distinct()

    room_code = request.GET.get('room_code')
    if room_code:
        rooms = rooms.filter(room_code__icontains = room_code)

    status_ids = request.GET.get('status_type')
    if status_ids and 'all' not in status_ids:
        rooms = rooms.filter(status__id__in=status_ids).distinct()

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        rooms = rooms.filter(price__gte=min_price, price__lte=max_price)

    return rooms

def listroom(request):

    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        user_not_login = "none"
        rooms = filter_rooms(request)
        allowed = rooms.exists()
        count = rooms.count()
        count_empty = rooms.filter(status="1").count()  # Count rooms with status "trống"
        count_full = rooms.filter(status="3").count()    # Count rooms with status "hết"
        count_waiting = rooms.filter(status="2").count() # Count rooms with status "Chờ"
        room_type = RoomType.objects.all()
        product_name = Product.objects.all()
        status_type = StatusType.objects.all()
        paginator = Paginator(rooms, 10)  # Paginate results
        page_number = request.GET.get('page')
        rooms_page = paginator.get_page(page_number)

        query_params = request.GET.copy()
        query_params.pop('page', None)  # Remove the 'page' parameter if it exists
        query_string = query_params.urlencode()  # Generate a clean query string
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        rooms_page = None
        return redirect('error_login')
    
    if user_profile.role != 'admin':
        return redirect('error_login')

    context = {'user_not_login': user_not_login,'count_empty': count_empty, 'count_full': count_full, 'count_waiting': count_waiting, 'product_names':product_name, 'rooms_page': rooms_page, 'allowed': allowed, 'count': count, 'profile': user_profile, 'room_types': room_type, 'status_types': status_type, 'query_string': query_string,}

    return render(request, 'apps/listroom.html', context)


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


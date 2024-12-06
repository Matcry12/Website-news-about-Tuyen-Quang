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
from django.core.paginator import Paginator
from home.templatetags.forms import RoomForm, RoomPicForm, ProductForm, ProductPicForm, RoomFormCreate, ProductFormCreate, SuperUserForm
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from openpyxl.styles import Border, Side, Font
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
import openpyxl


def news(request):
    news = new.objects.all()
    if request.user.is_authenticated:
        user_not_login = "none"
    else:
        user_not_login = "block"
    context = {'news': news, 'user_not_login': user_not_login}
    return render(request, 'apps/news.html', context)
def Cart(request):
    if request.user.is_authenticated:
        customer = request.user
        user_profile = UserProfile.objects.get(user=customer)
        # Corrected the field name to `customer`
        order_instance = order.objects.filter(room__product__owner=customer)
        if user_profile.role == "customer":
            order_instance = order.objects.filter(customer=customer)
        products = Product.objects.filter(owner=customer)
        user_not_login = "none"
        rooms = Room.objects.filter(product__owner = customer)

        paginator = Paginator(order_instance, 5)  # Show 5 orders per page
        page_number = request.GET.get('page')  # Get current page number from URL
        orders_page = paginator.get_page(page_number)
        
    else:
        order_instance = {}  # If the user is not authenticated, we don't need to query orders
        user_not_login = "block"
        user_profile = None
        products = None
        rooms = None
        orders_page = None  

    if request.method == 'POST':
        
        # Handle Product Excel Upload
        if 'hotel_excel' in request.FILES and user_profile.role == 'admin':
            excel_file = request.FILES['hotel_excel']
            
            # Open the uploaded Excel file
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            # Define the column headers for products
            headers = [
                'name', 'amountprice', 'owner (username)', 'onSale', 'detail', 'imageP',
                'categories (comma-separated category names)', 'room_types (comma-separated room type names)', 
                'product_type (comma-separated product type names)', 'location', 'maplocation', 'rate', 'phonecall'
            ]
            
            # Iterate over the rows in the sheet
            for row in sheet.iter_rows(min_row=2, values_only=True):
                product_data = dict(zip(headers, row))
                
                try:
                    # Get or create the owner User
                    owner = User.objects.get(username=product_data['owner (username)'])
                except ObjectDoesNotExist:
                    owner = None  # or handle exception if user does not exist
                
                # Create the Product instance
                product = Product.objects.create(
                    name=product_data['name'],
                    amountprice=product_data['amountprice'],
                    owner=owner,
                    onSale=product_data['onSale'],
                    detail=product_data['detail'],
                    imageP=product_data['imageP'],  # Handle image upload if necessary
                    location=product_data['location'],
                    maplocation=product_data['maplocation'],
                    rate=product_data['rate'],
                    phonecall=product_data['phonecall']
                )

                # Handle categories (comma-separated names)
                if product_data['categories (comma-separated category names)']:
                    categories = product_data['categories (comma-separated category names)'].split(',')
                    for category_name in categories:
                        _category, created = category.objects.get_or_create(name=category_name.strip())
                        product.categories.add(_category)

                # Handle room types (comma-separated names)
                if product_data['room_types (comma-separated room type names)']:
                    room_types = product_data['room_types (comma-separated room type names)'].split(',')
                    for room_type_name in room_types:
                        room_type, created = RoomType.objects.get_or_create(name=room_type_name.strip())
                        product.room_types.add(room_type)

                # Handle product types (comma-separated names)
                if product_data['product_type (comma-separated product type names)']:
                    product_types = product_data['product_type (comma-separated product type names)'].split(',')
                    for product_type_name in product_types:
                        product_type, created = ProductType.objects.get_or_create(name=product_type_name.strip())
                        product.product_type.add(product_type)

        # Handle Room Excel Upload
        if 'room_excel' in request.FILES:
            excel_file = request.FILES['room_excel']
            
            # Open the uploaded Excel file
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            # Define the column headers for rooms
            headers = [
                'room_code', 
                'price', 
                'room_type (comma-separated room type name)', 
                'status', 
                'rating', 
                'image'
            ]
            
            # Iterate over the rows in the sheet
            for row in sheet.iter_rows(min_row=2, values_only=True):
                room_data = dict(zip(headers, row))
                
                try:
                    # Get the Product instance by its name (assuming room belongs to a specific product)
                    products = Product.objects.filter(owner=customer)
                except ObjectDoesNotExist:
                    products = None  # or handle exception if product does not exist
                
                try:
                    # Get the Product instance by its name (assuming room belongs to a specific product)
                    room_type_name = room_data['room_type (comma-separated room type name)']

                    # Get or create the RoomType instance
                    room_type, created = RoomType.objects.get_or_create(name=room_type_name)
                except ObjectDoesNotExist:
                    room_type = None  # or handle exception if product does not exist

                # Create the Room instance
                if products.exists():
                    # Assuming you want to assign the first product (or you can handle this logic differently)
                    product = products.first()  # You can adjust this to select the appropriate product if necessary
                    
                    # Create the Room instance
                    room = Room.objects.create(
                        product=product,  # Assign the product to the room
                        room_code=room_data['room_code'],
                        price=room_data['price'],
                        room_type = room_type,
                        status=room_data['status'],
                        rating=room_data['rating'],
                        image=room_data['image'],  # Handle image upload if necessary
                    )
                else:
                    # Handle the case where no products are found for the owner (if needed)
                    pass

        return redirect('cart')

    context = {
        'orders_page': orders_page,
        'user_not_login': user_not_login,
        'order_instance': order_instance,  # Add the orders to the context for use in the template
        'products': products,
        'profile': user_profile,
        'rooms': rooms
    }

    return render(request, 'apps/cart.html', context)

def updateOrder(request):
    data = json.loads(request.body)

    order_id = data['orderId']
    action = data['action']

    Order = get_object_or_404(order, id=order_id)

    if action == 'true':
        Order.confirm = True
    elif action == 'false':
        Order.confirm = False
    Order.save()

    return JsonResponse("changed", safe=False)

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


def home(request):
    # Start with all products
    products = Product.objects.all()
    
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
    user_not_login = "none" if request.user.is_authenticated else "block"

    context = {
        'products': products,
        'categories': categories,
        'product_types': product_types,
        'room_types': room_types,
        'selected_categories': selected_categories,
        'selected_product_types': selected_product_types,
        'selected_room_types': selected_room_types,
        'user_not_login': user_not_login,
    }
    return render(request, 'apps/home.html', context)


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
    # Check if there are any superusers in the database
    allow = False
    if not User.objects.filter(is_superuser=True).exists():
        # If no superusers exist, allow any user to create a superuser
        allow = True
    context = {'allow': allow}
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


def newdetail(request):
    if request.user.is_authenticated:
        user_not_login = "none"
    else:
        user_not_login = "block"
    id = request.GET.get('id', '')
    news = new.objects.filter(id = id)
    context = {'news': news, 'user_not_login': user_not_login}
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

def delete_order(request, order_id):

    user_profile = UserProfile.objects.get(user=request.user)
    
    orderD = order.objects.get(id=order_id)
    if orderD.room.product.owner != request.user:
        return redirect('cart')
    orderD.delete()
    messages.success(request, "Order deleted successfully")
    return redirect('cart')

def delete_room(request, room_id):

    user_profile = UserProfile.objects.get(user=request.user)
    
    room = Room.objects.get(id=room_id)
    if room.product.owner != request.user:
        return redirect('cart')
    room.delete()
    messages.success(request, "Room deleted successfully")
    return redirect('cart')

def delete_hotel(request, hotel_id):

    user_profile = UserProfile.objects.get(user=request.user)
    
    hotel = Product.objects.get(id=hotel_id)
    if hotel.owner != request.user:
        return redirect('cart')
    hotel.delete()
    messages.success(request, "Hotel deleted successfully")
    return redirect('cart')
    
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

def filter_histories(request, user_profile):
    histories = history.objects.all()
    name = request.GET.get('name')
    if name:
        histories = histories.filter(room__product__name__icontains=name)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        histories = histories.filter(datebook__range=[start_date, end_date])
    elif start_date:
        histories = histories.filter(datebook__gte=start_date)
    elif end_date:
        histories = histories.filter(datebook__lte=end_date)

    cccd = request.GET.get('cccd')
    if cccd:
        histories = histories.filter(cccd=cccd)
    
    phone = request.GET.get('phonecall')
    if phone:
        histories = histories.filter(phonecall=phone)

    customer = request.GET.get('cname')
    if customer:
        histories = histories.filter(cname__icontains=customer)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        histories = histories.filter(room__price__gte=min_price, room__price__lte=max_price)

    if user_profile.role != 'admin':
        histories = histories.filter(
            customer=request.user
        ) | histories.filter(
            room__product__owner=request.user
        )
    
    return histories

def historylist(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        user_not_login = "none"
        histories = filter_histories(request, user_profile)
        allowed = histories.exists()
        count = histories.count()
        paginator = Paginator(histories, 10)  # Paginate results
        page_number = request.GET.get('page')
        histories_page = paginator.get_page(page_number)
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        histories_page = None
        return redirect('home')
    context = {'user_not_login': user_not_login, 'histories_page': histories_page, 'allowed': allowed, 'count': count,}
    return render(request, 'apps/historylist.html', context)

def completebooking(request):
    context = {}
    return render(request, 'apps/completebooking.html', context)

class AddRoomView(CreateView):
    model = Room
    form_class = RoomFormCreate
    template_name = 'apps/add_room.html'
    success_url = reverse_lazy('cart')

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if not authenticated

        # Check if the user owns any products
        products = Product.objects.filter(owner=request.user)
        if not products.exists():  # If the user has no products
            return redirect('cart')  # Redirect to the cart page

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        products = Product.objects.filter(owner=user)

        if products.exists():
            kwargs['initial'] = {'product': products.first()}
        else:
            kwargs['initial'] = {'product': None}
        
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        selected_product = form.cleaned_data['product']
        products = Product.objects.filter(owner=user)

        # Validate that the selected product belongs to the user
        if selected_product not in products:
            form.add_error('product', 'Bạn không thể chọn cơ sở lưu trú không phải của mình.')
            return self.form_invalid(form)

        # Proceed to save the room if validation passes
        room = form.save(commit=False)
        room.owner = user
        room.save()

        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, "Có lỗi khi bạn gửi bài. Vui lòng kiểm tra biểu mẫu và thử lại.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=self.request.user)
            products = Product.objects.filter(owner=self.request.user)
            context['profile'] = user_profile
            context['user_not_login'] = "none"
            context['product'] = products
        else:
            context['user_not_login'] = "block"
            context['profile'] = None
            context['product'] = None

        return context


class AddHotelView(CreateView):
    model = Product
    form_class = ProductFormCreate  # Use your custom form if necessary
    template_name = 'apps/add_hotel.html'
    success_url = reverse_lazy('cart')

    def form_valid(self, form):
        user_profile = UserProfile.objects.get(user=self.request.user)

        # Ensure the user is a seller (you can adjust this logic based on your app)
        if user_profile.role != 'seller':
            # Redirect to home or show a forbidden message if the user is not a seller
            return redirect('home')

        # Automatically assign the owner to the logged-in user
        product = form.save(commit=False)
        product.owner = self.request.user
        product.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional context if needed
        if self.request.user.is_authenticated:
            context['user_not_login'] = "none"
        else:
            context['user_not_login'] = "block"
            return redirect('home')  # Redirect if user is not authenticated

        return context
    
def export_history(request):
    # Fetch history data
    user_profile = UserProfile.objects.get(user=request.user)
    hisotry_user = filter_histories(request, user_profile)
    history_data = hisotry_user.values(
        'room__product__name',
        'room__room_code',  # Assuming Room model has a field 'room_code'
        'room__room_type__name',
        'room__price',
        'dateOrder',
        'outdateOrder',
        'datebook',
        'customer__username',  # Assuming 'username' is a field in your User model
        'cname',
        'address',
        'phonecall',
        'cccd',
    )

    # Convert QuerySet to DataFrame
    df = pd.DataFrame(list(history_data))

    # Rename columns for better readability
    df.rename(columns={
        'room__product__name': 'Cơ sở lưu trú',
        'room__room_code': 'Mã phòng',
        'room__room_type__name': 'Loại phòng',
        'room__price': 'Giá phòng (đồng)',
        'dateOrder': 'Ngày đặt phòng',
        'datebook': 'Ngày nhận phòng',
        'outdateOrder': 'Ngày trả phòng',
        'customer__username': 'Biệt danh khách hàng',
        'cname': 'Tên khách hàng',
        'address': 'Địa chỉ',
        'phonecall': 'Số điện thoại',
        'cccd': 'Căn cước công dân',
    }, inplace=True)

    # Format datetime columns to 'yyyy-mm-dd h:mm:ss'
    datetime_columns = ['Ngày đặt phòng', 'Ngày nhận phòng', 'Ngày trả phòng']
    for column in datetime_columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):  # Check if column is datetime
            df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')  # Apply format

    # Create Excel response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="history.xlsx"'

    # Create an Excel workbook and write the DataFrame to it
    wb = Workbook()
    ws = wb.active
    ws.title = "History"

    # Write DataFrame rows to the sheet
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)

            # Apply border to each cell
            border = Border(
                left=Side(border_style="thin"),
                right=Side(border_style="thin"),
                top=Side(border_style="thin"),
                bottom=Side(border_style="thin")
            )
            cell.border = border

            # Apply bold font to header row (first row)
            if r_idx == 1:
                cell.font = Font(bold=True)

    # Fit column widths to content
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Save the Excel file to the response
    wb.save(response)
    return response

def export_hotel(request):
    user_profile = UserProfile.objects.get(user=request.user)
    hotels = Product.objects.all()

    if user_profile.role != 'admin':
        hotels = hotels.filter(owner=request.user)
    hotels = Product.objects.annotate(room_count=Count('rooms'))
    hotel_data = []
    for hotel in hotels:
        room_types = ', '.join(room_type.name for room_type in hotel.room_types.all())
        try:
            full_owner_name = f"{hotel.owner.last_name} {hotel.owner.first_name}"
        except AttributeError:
            full_owner_name = "Unknown Owner"
        hotel_data.append({
            'Tên cơ sở lưu trú': hotel.name,
            'Địa chỉ': hotel.location,
            'Họ tên chủ cơ sở': full_owner_name,
            'Số phòng': hotel.room_count,
            'Loại phòng': room_types,  # Include room types here
            'Số điện thoại': hotel.phonecall,
            'Giá niêm yết':  hotel.amountprice,
            'Xếp hạng (sao)': hotel.rate,
        })

    # Convert to DataFrame
    df = pd.DataFrame(hotel_data)

    # Create Excel file (same as before)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="hotel_data.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Hotel Data"

    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)
            border = Border(
                left=Side(border_style="thin"),
                right=Side(border_style="thin"),
                top=Side(border_style="thin"),
                bottom=Side(border_style="thin")
            )
            cell.border = border
            if r_idx == 1:
                cell.font = Font(bold=True)

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width

    wb.save(response)
    return response

def generate_example_hotel(request):
    # Create a new workbook and a sheet
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Ví dụ cho cơ sở lưu trú"

    # Define the headers
    headers = [
        'name', 'amountprice', 'owner (username)', 'onSale', 'detail', 'imageP',
        'categories (comma-separated category names)', 'room_types (comma-separated room type names)', 
        'product_type (comma-separated product type names)', 'location', 'maplocation', 'rate', 'phonecall'
    ]
    
    # Add headers to the first row of the sheet
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Example data to be shown in the file (optional)
    example_data = [
        ["Cơ sở luu trú A", "100.000 - 200.000", "Ductam", True, "Khách sạn tuyệt đẹp bên cạnh bãi biển", "", "Bể bơi, Wifi", "Phòng đơn, Phòng đôi", "Khách sạn", "Tuyên Quang", "N/A", 5, "0123456789"],
        ["Cơ sở luu trú B", "300.000 - 500.000", "Duong", False, "Nhà nghỉ tuyệt vời", "", "Bãi đỗ xe", "Phòng VIP", "Nhà nghỉ", "Phú thọ", "N/A", 4, "0987654321"],
    ]

    # Add example data to the sheet (you can add more rows or leave it empty for the user to fill)
    for row_num, data in enumerate(example_data, 2):
        for col_num, value in enumerate(data, 1):
            cell = sheet.cell(row=row_num, column=col_num, value=value)

            # Apply border to each cell
            border = Border(
                left=Side(border_style="thin"),
                right=Side(border_style="thin"),
                top=Side(border_style="thin"),
                bottom=Side(border_style="thin")
            )
            cell.border = border

            # Apply bold font to header row (first row)
            if row_num == 1:
                cell.font = Font(bold=True)

    # Apply border to all header cells (first row)
    for col_num in range(1, len(headers) + 1):
        cell = sheet.cell(row=1, column=col_num)
        border = Border(
            left=Side(border_style="thin"),
            right=Side(border_style="thin"),
            top=Side(border_style="thin"),
            bottom=Side(border_style="thin")
        )
        cell.border = border

    # Adjust column widths to fit the content
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name (e.g., 'A', 'B', etc.)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2  # Add a little extra space
        sheet.column_dimensions[column].width = adjusted_width

    # Save the workbook to a response for download
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename="example_hotel_data.xlsx"'

    wb.save(response)
    return response

def generate_example_room(request):
    # Create a new workbook and a sheet
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Ví dụ cho phòng của cơ sở lưu trú"

    # Define the headers
    headers = [
        'room_code', 
        'price', 
        'room_type (comma-separated room type name)', 
        'status', 
        'rating', 
        'image'
    ]
    
    # Add headers to the first row of the sheet
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Example data to be shown in the file (optional)
    example_data = [
        ["0005", "1000000", "Phòng Đơn", True, "3", ""],
        ["0006", "5000000", "Phòng VIP", True, "2", ""],
    ]

    # Add example data to the sheet (you can add more rows or leave it empty for the user to fill)
    for row_num, data in enumerate(example_data, 2):
        for col_num, value in enumerate(data, 1):
            cell = sheet.cell(row=row_num, column=col_num, value=value)

            # Apply border to each cell
            border = Border(
                left=Side(border_style="thin"),
                right=Side(border_style="thin"),
                top=Side(border_style="thin"),
                bottom=Side(border_style="thin")
            )
            cell.border = border

            # Apply bold font to header row (first row)
            if row_num == 1:
                cell.font = Font(bold=True)

    # Apply border to all header cells (first row)
    for col_num in range(1, len(headers) + 1):
        cell = sheet.cell(row=1, column=col_num)
        border = Border(
            left=Side(border_style="thin"),
            right=Side(border_style="thin"),
            top=Side(border_style="thin"),
            bottom=Side(border_style="thin")
        )
        cell.border = border

    # Adjust column widths to fit the content
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name (e.g., 'A', 'B', etc.)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2  # Add a little extra space
        sheet.column_dimensions[column].width = adjusted_width

    # Save the workbook to a response for download
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename="example_room_data.xlsx"'

    wb.save(response)
    return response

def create_superuser(request):
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

    return render(request, 'apps/create_superuser.html', {'form': form})
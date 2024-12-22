from .views import *


def parse_price(price):
    return int(price.replace('.', '').strip())

def Order(request):
    if request.user.is_authenticated:
        customer = request.user
        user_profile = UserProfile.objects.get(user=customer)
        # Corrected the field name to `customer`
        order_instance = order.objects.filter(room__product__owner=customer)
        if user_profile.role == "customer":
            order_instance = order.objects.filter(customer=customer)
        user_not_login = "none"
        count = order_instance.count()

        paginator = Paginator(order_instance, 10) 
        page_number = request.GET.get('page')  # Get current page number from URL
        orders_page = paginator.get_page(page_number)
        
    else:
        order_instance = {}  # If the user is not authenticated, we don't need to query orders
        user_not_login = "block"
        user_profile = None
        orders_page = None  
        count = 0
        return redirect('error_login')

    if user_profile.role == 'admin':
        return redirect('error_login')

    context = {
        'orders_page': orders_page,
        'user_not_login': user_not_login,
        'order_instance': order_instance,  # Add the orders to the context for use in the template
        'profile': user_profile,
        'count': count,
        'page_name': 'order'
    }

    return render(request, 'apps/order.html', context)

def filter_room(request, customer):
    rooms = Room.objects.filter(product__owner = customer)

    room_code = request.GET.get('room_code')
    if room_code:
        rooms = rooms.filter(room_code__icontains=room_code)  # Use icontains for partial match

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price and max_price:
        rooms = rooms.filter(price__gte=min_price, price__lte=max_price)

    # Filter by selected room types (multiple selection allowed)
    room_ids = request.GET.getlist('room_type')
    if room_ids and 'all' not in room_ids:
        rooms = rooms.filter(room_type__id__in=room_ids).distinct()

    status_ids = request.GET.getlist('status_type')
    if status_ids and 'all' not in status_ids:
        rooms = rooms.filter(status__id__in=status_ids).distinct()

    return rooms

def Cart(request):
    if request.user.is_authenticated:
        customer = request.user
        user_profile = UserProfile.objects.get(user=customer)
        # Corrected the field name to `customer`
        products = Product.objects.filter(owner=customer)
        user_not_login = "none"
        rooms = filter_room(request, customer)
        categories = category.objects.all()
        room_type = RoomType.objects.all()
        status_type = StatusType.objects.all()
        hotel_type = ProductType.objects.all()

        paginator = Paginator(rooms, 15)  # Show 5 orders per page
        page_number = request.GET.get('page')  # Get current page number from URL
        room_page = paginator.get_page(page_number)

        query_params = request.GET.copy()
        query_params.pop('page', None)  # Remove the 'page' parameter if it exists
        query_string = query_params.urlencode()  # Generate a clean query string
        
    else:
        user_not_login = "block"
        user_profile = None
        room_type = None
        status_type = None
        products = None
        rooms = None
        room_page = None  
        return redirect('home')

    if user_profile.role == 'admin':
        return redirect('manage_hotel')
    
    if user_profile.role == 'customer':
        return redirect('home')

    if request.method == 'POST':
        
        # Handle Product Excel Upload
        if 'hotel_excel' in request.FILES and user_profile.role == 'admin':
            excel_file = request.FILES['hotel_excel']
            
            # Open the uploaded Excel file
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            # Define the column headers for products
            headers = [
                'Tên cơ sở lưu trú', 'Giá niêm yết', 'Chủ sở hữu (username)', 'Trạng thái', 'Mô tả',
                'Dịch vụ', 'Các loại phòng', 
                'Loại cơ sở lưu trú', 'Địa chỉ', 'Tọa độ', 'Đánh giá (sao)', 'Số điện thoại'
            ]
            
            # Iterate over the rows in the sheet
            for row in sheet.iter_rows(min_row=2, values_only=True):
                product_data = dict(zip(headers, row))
                
                if not product_data['Tên cơ sở lưu trú']:
                    continue

                try:
                    # Get or create the owner User
                    owner = User.objects.get(username=product_data['Chủ sở hữu (username)'])
                except ObjectDoesNotExist:
                    owner = None  # or handle exception if user does not exist
                
                # Create the Product instance
                product = Product.objects.create(
                    name=product_data['Tên cơ sở lưu trú'],
                    amountprice=product_data['Giá niêm yết'],
                    owner=owner,
                    onSale=product_data['Trạng thái'],
                    detail=product_data['Mô tả'],
                    location=product_data['Địa chỉ'],
                    maplocation=product_data['Tọa độ'],
                    rate=product_data['Đánh giá (sao)'],
                    phonecall=product_data['Số điện thoại']
                )

                # Handle categories (comma-separated names)
                if product_data['Dịch vụ']:
                    categories = product_data['Dịch vụ'].split(',')
                    for category_name in categories:
                        _category, created = category.objects.get_or_create(name=category_name.strip())
                        product.categories.add(_category)

                # Handle room types (comma-separated names)
                if product_data['Các loại phòng']:
                    room_types = product_data['Các loại phòng'].split(',')
                    for room_type_name in room_types:
                        room_type, created = RoomType.objects.get_or_create(name=room_type_name.strip())
                        product.room_types.add(room_type)

                # Handle product types (comma-separated names)
                if product_data['Loại cơ sở lưu trú']:
                    product_types = product_data['Loại cơ sở lưu trú'].split(',')
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
                'Mã số phòng', 
                'Giá thành', 
                'Loại phòng', 
                'Trạng thái', 
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
                    room_type_name = room_data['Loại phòng']

                    # Get or create the RoomType instance
                    room_type, created = RoomType.objects.get_or_create(name=room_type_name)
                except ObjectDoesNotExist:
                    room_type = None  # or handle exception if product does not exist

                try:
                    # Get the Product instance by its name (assuming room belongs to a specific product)
                    status_type_name = room_data['Trạng thái']

                    # Get or create the RoomType instance
                    status_type, created = StatusType.objects.get_or_create(name=status_type_name)
                except ObjectDoesNotExist:
                    status_type = None  # or handle exception if product does not exist


                # Create the Room instance
                if products.exists():
                    # Assuming you want to assign the first product (or you can handle this logic differently)
                    product = products.first()  # You can adjust this to select the appropriate product if necessary
                    
                    # Create the Room instance
                    room = Room.objects.create(
                        product=product,  # Assign the product to the room
                        room_code=room_data['Mã số phòng'],
                        price=room_data['Giá thành'],
                        room_type = room_type,
                        status=status_type,
                    )
                else:
                    # Handle the case where no products are found for the owner (if needed)
                    pass

        return redirect('cart')

    if user_profile.role == 'customer':
        return redirect('home')

    context = {
        'room_page': room_page,
        'user_not_login': user_not_login,
        'products': products,
        'room_types': room_type,
        'status_types': status_type,
        'profile': user_profile,
        'rooms': rooms,
        'query_string': query_string,
    }

    return render(request, 'apps/cart.html', context)

def updateOrder(request):
    data = json.loads(request.body)

    order_id = data['orderId']
    action = data['action']

    Order = get_object_or_404(order, id=order_id)

    if action == 'true':
        Order.confirm = True
        status_instance = StatusType.objects.get(name="Đang được sử dụng")
        Order.room.status = status_instance
        Order.room.save()
    elif action == 'false':
        status_instance = StatusType.objects.get(name="Chờ")
        Order.room.status = status_instance
        Order.room.save()
        Order.confirm = False
    Order.save()

    return JsonResponse("changed", safe=False)

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

def parse_amount_start(product):
    # Extract and convert amount_start to a numeric value
    amount_start = product.amountprice.split('-')[0]
    return float(amount_start.replace(',', '').replace('.', ''))

def filter_hotels(request):
    hotels = Product.objects.all()
    
    # Filter by username (partial match)
    name = request.GET.get('name')
    if name:
        hotels = hotels.filter(name__icontains=name)  # Use icontains for partial match

    owner = request.GET.get('owner')
    if owner:
        hotels = hotels.filter(owner__icontains=owner)


    price = request.GET.get('price')
    if price and price != 'all':

        start_price = None
        end_price = None

        if price == '1':
            end_price = '500.000'
        if price == '2':
            start_price = '500.000'
            end_price = '1.000.000'
        if price == '3':
            start_price = '1.000.000'

        if end_price or start_price:  # Check if either price is provided
            filtered_hotels = []

            if end_price:
                end = parse_price(end_price)
                for item in hotels:
                    amount_start, amount_end = map(parse_price, item.amountprice.split('-'))
                    if amount_start <= end:
                        filtered_hotels.append(item)

            if start_price:
                start = parse_price(start_price)
                for item in hotels:
                    amount_start, amount_end = map(parse_price, item.amountprice.split('-'))
                    if start <= amount_start:
                        filtered_hotels.append(item)

            # Ensure only unique IDs are filtered when both conditions are applied
            filtered_ids = list({hotel.id for hotel in filtered_hotels})
            hotels = hotels.filter(id__in=filtered_ids)

    category_ids = request.GET.getlist('category')
    if category_ids and 'all' not in category_ids:
        hotels = hotels.filter(categories__id__in=category_ids).distinct()

    # Filter by selected room types (multiple selection allowed)
    room_ids = request.GET.getlist('room')
    if room_ids and 'all' not in room_ids:
        hotels = hotels.filter(room_types__id__in=room_ids).distinct()

    # Filter by selected hotel types
    hotel_type_id = request.GET.get('hotel')
    if hotel_type_id and hotel_type_id != 'all':
        hotels = hotels.filter(product_type__id=hotel_type_id)

    # Filter by rating
    rate = request.GET.get('rate')
    if rate and rate != 'all':
        if rate.isdigit():
            hotels = hotels.filter(rate__gte=int(rate))

    return hotels

def manage_hotel(request):
    
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'admin':
            return redirect('home')
        user_not_login = "none"
        products = filter_hotels(request)
        sorted_hotels = sorted(products, key=parse_amount_start)
        categories = category.objects.all()
        room_type = RoomType.objects.all()
        hotel_type = ProductType.objects.all()

        allowed = products.exists()
        count = products.count()
        paginator = Paginator(sorted_hotels, 10)  # Paginate results
        page_number = request.GET.get('page')
        hotels_page = paginator.get_page(page_number)

        query_params = request.GET.copy()
        query_params.pop('page', None)  # Remove the 'page' parameter if it exists
        query_string = query_params.urlencode()  # Generate a clean query string
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        hotels_page = None
        return redirect('home')
    if request.method == 'POST':
        
        # Handle Product Excel Upload
        if 'hotel_excel' in request.FILES and user_profile.role == 'admin':
            excel_file = request.FILES['hotel_excel']
            
            # Open the uploaded Excel file
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            # Define the column headers for products
            headers = [
                'Tên cơ sở lưu trú', 'Giá niêm yết', 'Chủ sở hữu (username)', 'Trạng thái', 'Mô tả',
                'Dịch vụ', 'Các loại phòng', 
                'Loại cơ sở lưu trú', 'Địa chỉ', 'Tọa độ', 'Đánh giá (sao)', 'Số điện thoại'
            ]
            
            # Iterate over the rows in the sheet
            for row in sheet.iter_rows(min_row=2, values_only=True):
                product_data = dict(zip(headers, row))
                
                if not product_data['Tên cơ sở lưu trú']:
                    continue

                try:
                    # Get or create the owner User
                    owner = User.objects.get(username=product_data['Chủ sở hữu (username)'])
                except ObjectDoesNotExist:
                    owner = None  # or handle exception if user does not exist
                
                # Create the Product instance
                product = Product.objects.create(
                    name=product_data['Tên cơ sở lưu trú'],
                    amountprice=product_data['Giá niêm yết'],
                    owner=owner,
                    onSale=product_data['Trạng thái'],
                    detail=product_data['Mô tả'],
                    location=product_data['Địa chỉ'],
                    maplocation=product_data['Tọa độ'],
                    rate=product_data['Đánh giá (sao)'],
                    phonecall=product_data['Số điện thoại']
                )

                # Handle categories (comma-separated names)
                if product_data['Dịch vụ']:
                    categories = product_data['Dịch vụ'].split(',')
                    for category_name in categories:
                        _category, created = category.objects.get_or_create(name=category_name.strip())
                        product.categories.add(_category)

                # Handle room types (comma-separated names)
                if product_data['Các loại phòng']:
                    room_types = product_data['Các loại phòng'].split(',')
                    for room_type_name in room_types:
                        room_type, created = RoomType.objects.get_or_create(name=room_type_name.strip())
                        product.room_types.add(room_type)

                # Handle product types (comma-separated names)
                if product_data['Loại cơ sở lưu trú']:
                    product_types = product_data['Loại cơ sở lưu trú'].split(',')
                    for product_type_name in product_types:
                        product_type, created = ProductType.objects.get_or_create(name=product_type_name.strip())
                        product.product_type.add(product_type)
            return redirect('manage_hotel')
    
    context = {'user_not_login': user_not_login, 'hotels_page': hotels_page, 'allowed': allowed, 'count': count, 'profile': user_profile, 'categories': categories, 'hotel_type': hotel_type, 'room_type': room_type, 'query_string': query_string,}

    return render(request, 'apps/manage_hotel.html', context)

def filter_room_detail(request, hotel_id):
    rooms = Room.objects.filter(product__id = hotel_id)

    room_code = request.GET.get('room_code')
    if room_code:
        rooms = rooms.filter(room_code__icontains=room_code)  # Use icontains for partial match

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price and max_price:
        rooms = rooms.filter(price__gte=min_price, price__lte=max_price)

    # Filter by selected room types (multiple selection allowed)
    room_ids = request.GET.getlist('room_type')
    if room_ids and 'all' not in room_ids:
        rooms = rooms.filter(room_type__id__in=room_ids).distinct()

    status_ids = request.GET.getlist('status_type')
    if status_ids and 'all' not in status_ids:
        rooms = rooms.filter(status__id__in=status_ids).distinct()

    return rooms

def detail_hotel(request, hotel_id):
    if request.user.is_authenticated:
        customer = request.user
        user_profile = UserProfile.objects.get(user=customer)
        # Corrected the field name to `customer`
        products = Product.objects.filter(id=hotel_id)
        user_not_login = "none"
        rooms = filter_room_detail(request, hotel_id)
        room_type = RoomType.objects.all()
        status_type = StatusType.objects.all()
        paginator = Paginator(rooms, 15)  # Show 5 orders per page
        page_number = request.GET.get('page')  # Get current page number from URL
        room_page = paginator.get_page(page_number)
        
    else:
        user_not_login = "block"
        user_profile = None
        room_type = None
        status_type = None
        products = None
        rooms = None
        room_page = None  

    if user_profile.role != 'admin':
        return redirect('home')

    context = {
        'room_page': room_page,
        'user_not_login': user_not_login,
        'products': products,
        'room_types': room_type,
        'status_types': status_type,
        'profile': user_profile,
        'rooms': rooms,
    }

    return render(request, 'apps/detail_hotel.html', context)
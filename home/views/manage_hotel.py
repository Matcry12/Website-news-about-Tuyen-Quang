from .views import *

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
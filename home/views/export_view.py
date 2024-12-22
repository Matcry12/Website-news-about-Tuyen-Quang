from .views import *

def parse_amount_start(product):
    # Extract and convert amount_start to a numeric value
    amount_start = product.amountprice.split('-')[0]
    return float(amount_start.replace(',', '').replace('.', ''))

def filter_hotels(request):
    hotels = Product.objects.annotate(room_count=Count('rooms'))
    
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

    sorted_hotels = sorted(hotels, key=parse_amount_start)
    return sorted_hotels

def export_hotel(request):
    user_profile = UserProfile.objects.get(user=request.user)
    

    if user_profile.role != 'admin':
        hotels = hotels.filter(owner=request.user)
    hotels = filter_hotels(request)
    hotel_data = []
    for hotel in hotels:
        room_types = ', '.join(room_type.name for room_type in hotel.room_types.all())
        try:
            full_owner_name = f"{hotel.owner.last_name} {hotel.owner.first_name}"
        except AttributeError:
            full_owner_name = "Vô chủ"
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

def filter_users(request, user_profile):
    users = UserProfile.objects.all()

    # Filter by username (partial match)
    name = request.GET.get('name')
    if name:
        users = users.filter(user__username__icontains=name)  # Use icontains for partial match

    # Filter by CCCD (partial match)
    cccd = request.GET.get('cccd')
    if cccd:
        users = users.filter(cccd__icontains=cccd)  # Use icontains for partial match
    
    # Filter by phone number (partial match)
    phone = request.GET.get('phonecall')
    if phone:
        users = users.filter(phonecall__icontains=phone)  # Use icontains for partial match

    # Filter by full name (concatenated first and last name, partial match)
    fullname = request.GET.get('fullname')
    if fullname:
        users = users.annotate(
            full_name=Concat(F('user__last_name'), Value(' '), F('user__first_name'))
        ).filter(
            full_name__icontains=fullname  # Partial match for full name
        )

    # Filter by email (partial match)
    email = request.GET.get('email')
    if email:
        users = users.filter(user__email__icontains=email)  # Use icontains for partial match
    
    role_ids = request.GET.getlist('role')
    if 'all' not in role_ids:
        if '1' in role_ids:
            users = users.filter(role='customer')
        if '2' in role_ids:
            users = users.filter(role='seller')
        if '3' in role_ids:
            users = users.filter(role='admin')


    # If the user role is not 'admin', restrict the result
    if user_profile.role != 'admin':
        return None
    
    return users

def export_account(request):
    # Fetch history data
    user_profile = UserProfile.objects.get(user=request.user)
    users = filter_users(request, user_profile)
    
    user_data = users.annotate(
        full_name=Concat(F('user__last_name'), Value(' '), F('user__first_name')),
        product_name = Value('N/a')
    ).values(
        'user__username',
        'role',
        'product_name',
        'full_name',     
        'user__email', 
        'phonecall',
        'cccd',
        'birthday',
        'base_password',
        'date_created',
        
    )

    product_mapping = defaultdict(list)
    for product in Product.objects.select_related('owner').all():
        product_mapping[product.owner.username].append(product.name)

    for user in user_data:
        username = user['user__username']
        user['product_name'] = ', '.join(product_mapping.get(username, ['N/A']))

    df = pd.DataFrame(list(user_data))

    df['user__email'].replace('', 'N/a', inplace=True)
    df['base_password'].replace({None: 'Tài khoản đã đổi mật khẩu'}, inplace=True)
    df['base_password'].replace('None', 'Tài khoản đã đổi mật khẩu', inplace=True)
    df['base_password'].replace('none', 'Tài khoản đã đổi mật khẩu', inplace=True)
    # Rename columns for better readability
    df.rename(columns={
        'user__username': 'Tên tài khoản',
        'role': 'Vai trò',
        'product_name': 'Tên cơ sở lưu trú',
        'full_name': 'Họ tên',      
        'birthday': 'Ngày sinh',
        'user__email': 'Email',
        'cccd': 'Căn cước công dân',
        'phonecall': 'Số điện thoại',
        'base_password': 'Mật khẩu',
        'date_created': 'Ngày tạo',
    }, inplace=True)

    # Format datetime columns to 'yyyy-mm-dd h:mm:ss'
    datetime_columns = ['Ngày sinh', 'Ngày tạo']
    for column in datetime_columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):  # Check if column is datetime
            df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')  # Apply format

    # Create Excel response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="accounts.xlsx"'

    # Create an Excel workbook and write the DataFrame to it
    wb = Workbook()
    ws = wb.active
    ws.title = "Accounts"

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

def export_room(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role != 'admin':
        return redirect('home')
    
    rooms = filter_rooms(request)

    
    room_data = rooms.values(
        'id',
        'product__name',
        'room_type__name',      
        'room_code',
        'price',
        'status__name',
    )
    # Convert QuerySet to DataFrame
    df = pd.DataFrame(list(room_data))

    df.drop(columns=['id'], inplace=True)

    # Rename columns for better readability
    df.rename(columns={
        'product__name': 'Cơ sở lưu trú',
        'room_type__name': 'Loại phòng',      
        'room_code': 'Số phòng',
        'price': 'Giá',
        'status__name': 'Tình trạng',
    }, inplace=True)

    # Create Excel response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="rooms.xlsx"'

    # Create an Excel workbook and write the DataFrame to it
    wb = Workbook()
    ws = wb.active
    ws.title = "Rooms"

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

def export_new_password(request):
    # Retrieve the reset results from the session
    reset_results = request.session.get("reset_results", [])

    # Generate the Excel file
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Password Resets"

    # Add headers
    headers = ["Tên tài khoản", "Tên đệm", "Tên riêng", "Email", "Mật khẩu mới"]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num, value=header)

        # Apply bold font to header row
        cell.font = Font(bold=True)

    # Add rows for each user
    for row_num, result in enumerate(reset_results, start=2):  # Start from row 2
        sheet.cell(row=row_num, column=1, value=result.get("account"))
        sheet.cell(row=row_num, column=2, value=result.get("last_name"))
        sheet.cell(row=row_num, column=3, value=result.get("first_name"))
        sheet.cell(row=row_num, column=4, value=result.get("email"))
        sheet.cell(row=row_num, column=5, value=result.get("new_password"))

    # Define the border style
    thin_border = Border(
        left=Side(border_style="thin"),
        right=Side(border_style="thin"),
        top=Side(border_style="thin"),
        bottom=Side(border_style="thin")
    )

    # Apply borders to all cells
    for row in sheet.iter_rows():
        for cell in row:
            cell.border = thin_border

    # Adjust column widths
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if cell.value and len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = max_length + 2  # Add extra space for better appearance
        sheet.column_dimensions[column].width = adjusted_width

    # Save the workbook to an in-memory file
    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)  # Move to the beginning of the file

    # Return the file as a response
    response = HttpResponse(
        excel_file,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Password_Resets.xlsx"
    return response

from .views import *

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

def export_account(request):
    # Fetch history data
    user_profile = UserProfile.objects.get(user=request.user)
    users = filter_users(request, user_profile)
    
    user_data = users.annotate(
        full_name=Concat(F('user__last_name'), Value(' '), F('user__first_name'))
    ).values(
        'user__username',
        'full_name',      
        'birthday',
        'user__email',
        'cccd',
        'phonecall',
        'date_created',
    )

    # Convert QuerySet to DataFrame
    df = pd.DataFrame(list(user_data))

    # Rename columns for better readability
    df.rename(columns={
        'user__username': 'Tên tài khoản',
        'full_name': 'Họ tên',      
        'birthday': 'Ngày sinh',
        'user__email': 'Email',
        'cccd': 'Căn cước công dân',
        'phonecall': 'Số điện thoại',
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
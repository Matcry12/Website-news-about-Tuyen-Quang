from .views import *

def parse_price_start(history):
    # Extract and convert amount_start to a numeric value
    amount_start = history.room.price.split('-')[0]
    return float(amount_start.replace(',', '').replace('.', ''))

def filter_histories(request, user_profile):
    histories = history.objects.all()
    name = request.GET.get('name')
    if name:
        histories = histories.filter(room__product__name__icontains=name)

    _start_date = request.GET.get('start_date')
    _end_date = request.GET.get('end_date')

    if _start_date != '' and _start_date != None:
        start_date = datetime.strptime(_start_date, "%d/%m/%Y")
    else:
        start_date = _start_date

    if _end_date != '' and _end_date != None:
        end_date = datetime.strptime(_end_date, "%d/%m/%Y")
    else:
        end_date = _end_date
        

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

        query_params = request.GET.copy()
        query_params.pop('page', None)  # Remove the 'page' parameter if it exists
        query_string = query_params.urlencode()  # Generate a clean query string
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        histories_page = None
        return redirect('error_login')
    context = {'user_not_login': user_not_login, 'histories_page': histories_page, 'allowed': allowed, 'count': count, 'profile': user_profile, 'query_string': query_string,}
    return render(request, 'apps/historylist.html', context)

def completebooking(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        user_not_login = "none"
        # Fetch the UserProfile for the authenticated user
    else:
        user_not_login = "block"
        user_profile = None
    context = {'profile': user_profile, 'user_not_login':user_not_login}
    return render(request, 'apps/completebooking.html', context)

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
        'method',
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
        'method': 'Phương thức thanh toán',
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
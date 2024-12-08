from .views import *

def generate_example_hotel(request):
    # Create a new workbook and a sheet
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Ví dụ cho cơ sở lưu trú"

    # Define the headers
    headers = [
        'Tên cơ sở lưu trú', 'Giá niêm yết', 'Chủ sở hữu (username)', 'Trạng thái', 'Mô tả',
        'Dịch vụ', 'Các loại phòng', 
        'Loại cơ sở lưu trú', 'Địa chỉ', 'Tọa độ', 'Đánh giá (sao)', 'Số điện thoại'
    ]
    
    # Add headers to the first row of the sheet
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Example data to be shown in the file (optional)
    example_data = [
        ["Cơ sở luu trú A", "100.000 - 200.000", "Ductam", True, "Khách sạn tuyệt đẹp bên cạnh bãi biển", "Bể bơi, Wifi", "Phòng đơn, Phòng đôi", "Khách sạn", "Tuyên Quang", "N/A", 5, "0123456789"],
        ["Cơ sở luu trú B", "300.000 - 500.000", "Duong", False, "Nhà nghỉ tuyệt vời", "Bãi đỗ xe", "Phòng VIP", "Nhà nghỉ", "Phú thọ", "N/A", 4, "0987654321"],
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
        'Mã số phòng', 
        'Giá thành', 
        'Loại phòng', 
        'Trạng thái', 
    ]
    
    # Add headers to the first row of the sheet
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Example data to be shown in the file (optional)
    example_data = [
        ["0005", "1000000", "Phòng Đơn", 'Trống'],
        ["0006", "5000000", "Phòng VIP", 'Trống',],
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

def generate_example_account(request):
    # Create a new workbook and a sheet
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Ví dụ cho tài khoản"

    # Define the headers
    headers = [
        'Tên tài khoản (username)', 
        'Email', 
        'Tên riêng', 
        'Tên đệm', 
        'Số điện thoại',
        'Mật khẩu',
    ]
    
    # Add headers to the first row of the sheet
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Example data to be shown in the file (optional)
    example_data = [
        ["Triet", "fdtywadw@gmail.com", "Triết", "Nguyễn Anh", "0335788907", "123456"],
        ["Phong", "N/a", "Hoàng Phong", "Nguyễn Vũ", "N/a", "123456"],
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
    response['Content-Disposition'] = 'attachment; filename="example_accounts_data.xlsx"'

    wb.save(response)
    return response
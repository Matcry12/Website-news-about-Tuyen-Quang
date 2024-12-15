from django import forms
from home.models import Room, Product, User, UserProfile
from django.conf import settings

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['product', 'room_code', 'price', 'room_type', 'status', 'rating']
        labels = {
            'product': ('Cơ sở lưu trú'),
            'room_code': ('Mã phòng'),
            'price': ('Giá'),
            'room_type': ('Loại phòng'),
            'status': ('Trạng thái'),
            'rating': ('Đánh giá'),
        }

class RoomFormCreate(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['product', 'room_code', 'price', 'room_type', 'status', 'rating', 'image']
        labels = {
            'product': ('Cơ sở lưu trú'),
            'room_code': ('Mã phòng'),
            'price': ('Giá'),
            'room_type': ('Loại phòng'),
            'status': ('Trạng thái'),
            'rating': ('Đánh giá'),
            'image': ('Ảnh phòng'),
        }

class RoomPicForm(forms.ModelForm):
    image = forms.ImageField(label="Ảnh Phòng")
    class Meta:
        model = Room
        fields = ('image', )

class ProductFormCreate(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 
            'amountprice', 
            'onSale', 
            'detail', 
            'imageP', 
            'categories', 
            'room_types', 
            'product_type', 
            'location', 
            'maplocation', 
            'rate', 
            'phonecall'
        ]
        labels = {
            'name': 'Tên cơ sở lưu trú',
            'amountprice': 'Giá',
            'onSale': 'Đang bán',
            'detail': 'Chi tiết',
            'imageP': 'Hình ảnh',
            'categories': 'Danh mục',
            'room_types': 'Loại phòng',
            'product_type': 'Loại sản phẩm',
            'location': 'Vị trí',
            'maplocation': 'Bản đồ',
            'rate': 'Đánh giá',
            'phonecall': 'Số điện thoại',
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 
            'amountprice', 
            'onSale', 
            'detail', 
            'categories', 
            'room_types', 
            'product_type', 
            'location', 
            'maplocation', 
            'rate', 
            'phonecall'
        ]
        labels = {
            'name': 'Tên cơ sở lưu trú',
            'amountprice': 'Giá',
            'onSale': 'Đang bán',
            'detail': 'Chi tiết',
            'categories': 'Danh mục',
            'room_types': 'Loại phòng',
            'product_type': 'Loại sản phẩm',
            'location': 'Vị trí',
            'maplocation': 'Bản đồ',
            'rate': 'Đánh giá',
            'phonecall': 'Số điện thoại',
        }

        
class ProductPicForm(forms.ModelForm):
    imageP = forms.ImageField(label="Ảnh Phòng")
    
    class Meta:
        model = Product
        fields = ('imageP', )

class SuperUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Tên tài khoản',
            'email': 'Email',
            'password': 'Mật khẩu',
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['cccd', 'birthday', 'phonecall', 'profile_image']
        labels = {
            'cccd': 'Căn cước công dân',
            'birthday': 'Ngày sinh',
            'phonecall': 'Số điện thoại',
            'profile_image': 'Ảnh đại diện',
        }
        widgets = {
            'cccd': forms.TextInput(attrs={
                'class': 'form-control form-outline',
                'placeholder': 'Nhập căn cước công dân',
                'pattern': r'^\d{12}$',  # Pattern for 12-digit CCCD
                'oninvalid': "this.setCustomValidity('Căn cước công dân phải là 12 chữ số.')",
                'oninput': "this.setCustomValidity('')"
            }),
            'birthday': forms.DateInput(attrs={
                'class': 'form-control form-outline',
                'type': 'date',
                'placeholder': 'Ngày sinh (d/m/y)',
                'oninvalid': "this.setCustomValidity('Vui lòng nhập ngày sinh hợp lệ.')",
                'oninput': "this.setCustomValidity('')",
            }),
            'phonecall': forms.TextInput(attrs={
                'class': 'form-control form-outline',
                'placeholder': 'Nhập số điện thoại',
                'pattern': r'^(\\+84|0)[3|5|7|8|9][0-9]{8}$',  # Example phone number pattern (Vietnam)
                'oninvalid': "this.setCustomValidity('Số điện thoại không hợp lệ.')",
                'oninput': "this.setCustomValidity('')"
            }),
            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-outline',
                'accept': 'image/*',  # Allow only image files
            }),
        }

    # Add custom `input_formats` for the `birthday` field
    birthday = forms.DateField(
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-outline',
            'placeholder': 'Ngày sinh (dd/mm/yyyy)',
            'type': 'text',  # Use text instead of date to enforce custom format
            'oninvalid': "this.setCustomValidity('Vui lòng nhập ngày sinh hợp lệ (dd/mm/yyyy).')",
            'oninput': "this.setCustomValidity('')",
        }),
        required=True
    )



class UserEditForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-outline', 'placeholder': 'Nhập mật khẩu mới'}),
        required=False
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-outline', 'placeholder': 'Xác nhận mật khẩu'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Tên tài khoản',
            'email': 'Email',
            'first_name': 'Tên riêng',
            'last_name': 'Họ',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-outline', 
                'placeholder': 'Nhập tên tài khoản', 
                'required': 'required', 
                'oninvalid': "this.setCustomValidity('Vui lòng nhập tên tài khoản')",
                'oninput': "this.setCustomValidity('')"
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-outline',
                'placeholder': 'Nhập email',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-outline', 
                'placeholder': 'Nhập tên riêng', 
                'required': 'required', 
                'oninvalid': "this.setCustomValidity('Vui lòng nhập tên riêng')",
                'oninput': "this.setCustomValidity('')"
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-outline', 
                'placeholder': 'Nhập tên họ', 
                'required': 'required', 
                'oninvalid': "this.setCustomValidity('Vui lòng nhập tên họ')",
                'oninput': "this.setCustomValidity('')"
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Check if both passwords match
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Mật khẩu không khớp')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # Update password if password1 is provided
        if self.cleaned_data['password1']:
            user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user
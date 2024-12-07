from django import forms
from home.models import Room, Product, User, UserProfile

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

class UserEditForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mật khẩu mới'}),
        required=False
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={'placeholder': 'Xác nhận mật khẩu'}),
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
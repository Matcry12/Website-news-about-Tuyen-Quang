from django import forms
from home.models import Room, Product, User

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
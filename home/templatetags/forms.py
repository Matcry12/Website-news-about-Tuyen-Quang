from django import forms
from home.models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['product', 'room_code', 'price', 'room_type', 'status', 'rating']
        labels = {
            'product': ('Sản phẩm'),
            'room_code': ('Mã phòng'),
            'price': ('Giá'),
            'room_type': ('Loại phòng'),
            'status': ('Trạng thái'),
            'rating': ('Đánh giá'),
        }
class RoomPicForm(forms.ModelForm):
    image = forms.ImageField(label="Ảnh Phòng")
    
    class Meta:
        model = Room
        fields = ('image', )
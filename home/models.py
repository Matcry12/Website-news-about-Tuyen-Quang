from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.timezone import now
# User Creation Form
class CreationUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
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

# Category model
class category(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class RoomType(models.Model):
    code = models.CharField(max_length=10, unique=True)  # Unique identifier for the room type
    name = models.CharField(max_length=100)  # Display name for the room type
    
    class Meta:
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"

    def __str__(self):
        return self.name

class ProductType(models.Model):
    name = models.CharField(max_length=100)  # Display name for the room type

    def __str__(self):
        return self.name

# Product model (Hotel)
class Product(models.Model):
    name = models.CharField(max_length=1000)
    amountprice = models.CharField(max_length=255, blank=False, default='0')
    owner =  models.OneToOneField(User, on_delete=models.CASCADE, related_name='products')
    onSale = models.BooleanField(default=False)
    detail = models.TextField(null=True, blank=True)
    imageP = models.ImageField(null=True, blank=True, upload_to="hotels/")
    categories = models.ManyToManyField(category, blank=True)
    room_types = models.ManyToManyField(RoomType, blank=True)  # Allows multiple room types
    product_type = models.ManyToManyField(ProductType, blank=True)
    location = models.CharField(max_length=255)
    maplocation = models.CharField(max_length=255, default='N/A')
    rate = models.IntegerField(null=True)
    phonecall = models.CharField(max_length=255, blank=False, default='0')

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.imageP.url
        except:
            url = ''
        return url
    def ownerName(self):
        return f"{self.owner.last_name} {self.owner.first_name}"
    
class StatusType(models.Model):
    name = models.CharField(max_length=100)  # Display name for the room type

    def __str__(self):
        return self.name

class Room(models.Model):
    product = models.ForeignKey(Product, related_name='rooms', on_delete=models.CASCADE)  # Link each room to a hotel
    room_code = models.CharField(max_length=255)  # Unique code for each room
    price = models.IntegerField(null=True, default=0)
    room_type = models.ForeignKey(
        RoomType, on_delete=models.SET_NULL, null=True, related_name='rooms', to_field='code'
    )  # Reference the 'code' field of RoomType
    status = models.ForeignKey(StatusType, on_delete=models.SET_NULL, null=True, related_name='rooms')
    rating = models.IntegerField(null=True)
    image = models.ImageField(null=True, blank=True, upload_to="rooms/", default='default-image.png')

    def __str__(self):
        return f"{self.product.name} - {self.room_type.name if self.room_type else 'Unknown'} - {self.room_code}"

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    def roomCode(self):
        # Remove "Khách sạn" from the hotel name if it exists
        product_name = self.product.name.replace('Khách sạn ', '')
        
        # Split the name into words and take the first character of each word
        name_parts = product_name.split()
        initials = ''.join([word[0].upper() for word in name_parts])  # Take the first letter of each word and convert to uppercase
        
        # Combine the initials and room type code
        room_type_code = self.room_type.code if self.room_type else "NA"
        room_code = f"{initials}{room_type_code}"
        
        return room_code
    
    def roomName(self):
        return f"{self.room_type.name if self.room_type else 'Unknown'}"
        
    
# Order model
class order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    dateOrder = models.DateTimeField(auto_now_add=True)
    outdateOrder = models.DateTimeField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    confirm = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=False, default="N/A")
    cname = models.CharField(max_length=255, blank=False, default="N/A")
    phonecall = models.CharField(max_length=255, blank=False, default='0')
    cccd = models.CharField(max_length=255, blank=False, default='0')
    datebook = models.DateTimeField(null=True, blank=False)
    method = models.CharField(max_length=255, blank=False, default="N/A")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer} ({'Complete' if self.confirm else 'Pending'})"

class history(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    dateOrder = models.DateTimeField(null=True, blank=True)  # Original order creation date
    outdateOrder = models.DateTimeField(auto_now_add=True)  # Timestamp of deletion
    datebook = models.DateTimeField(null=True, blank=False)
    address = models.CharField(max_length=255, blank=False, default="N/A")
    cname = models.CharField(max_length=255, blank=False, default="N/A")
    phonecall = models.CharField(max_length=255, blank=False, default="0")
    cccd = models.CharField(max_length=255, blank=False, default='0')
    method = models.CharField(max_length=255, blank=False, default="N/A")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"History for Order #{self.id} - {self.customer}"

# Cart model
class cart(models.Model):
    order = models.ForeignKey(order, on_delete=models.SET_NULL, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        order_id = self.order.id if self.order else "No Order"
        room_id = self.room.id if self.room else "No Room"
        return f"Cart for Order #{order_id} (Room #{room_id}) - Added on {self.date_added}"

# News model
class new(models.Model):
    title = models.CharField(max_length=1000)
    detail = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="news/")

    def __str__(self):
        return self.title

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

# User Profile model
class UserProfile(models.Model):
    ROLE_TYPE_CHOICES = [
        ('seller', 'Chủ CS lưu trú'),
        ('customer', 'Khách hàng'),
        ('admin', 'Người quản lí'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cccd = models.CharField(max_length=255, blank=False, default='N/a')
    birthday = models.DateTimeField(null=True, blank=False)
    phonecall = models.CharField(max_length=255, blank=False, default="N/a")
    date_created = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=255, choices=ROLE_TYPE_CHOICES, default='customer',)
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)
    data_modified = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to="profiles/")
    base_password = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url
    

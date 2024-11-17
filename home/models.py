from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# User Creation Form
class CreationUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-outline', 'placeholder': 'Nhập tên tài khoản'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-outline', 'placeholder': 'Nhập email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-outline', 'placeholder': 'Nhập tên riêng'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-outline', 'placeholder': 'Nhập tên họ'}),
        }
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        # Create UserProfile after saving user
        role = self.cleaned_data.get('role', 'customer')  # Default role is 'customer'
        UserProfile.objects.create(user=user, role=role)
        return user

# Category model
class category(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

# Product model (Hotel)
class Product(models.Model):
    name = models.CharField(max_length=1000)
    owner = models.CharField(max_length=1000, default='N/A')
    amountprice = models.CharField(max_length=255, blank=False, default='0')
    onSale = models.BooleanField(default=False)
    detail = models.TextField(null=True, blank=True)
    imageP = models.ImageField(null=True, blank=True)
    categories = models.ManyToManyField(category, blank=True)
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

# Room model linked to Product
class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('1', 'Phòng đơn'),
        ('2', 'Phòng đôi'),
        ('3', 'Phòng ba'),
        ('2bed', 'Phòng 2 giường'),
        ('3bed', 'Phòng 3 giường'),
        ('vip', 'Phòng VIP'),
    ]

    product = models.ForeignKey(Product, related_name='rooms', on_delete=models.CASCADE)  # Link each room to a hotel
    room_code = models.CharField(max_length=255)  # Unique code for each room
    price = models.IntegerField(null=True, default=0)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)  # Room type
    status = models.BooleanField(default=True)  # True if on sale
    rating = models.IntegerField(null=True)
    image = models.ImageField(null=True, blank=True, upload_to="rooms/")

    def __str__(self):
        return f"{self.product.name} - {self.get_room_type_display()}"

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
        room_type_code = self.room_type
        room_code = f"{initials}{room_type_code}"
        
        return room_code
    
    def roomName(self):
        return f"{self.get_room_type_display()}"

        
    
# Order model
class order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    dateOrder = models.DateTimeField(auto_now_add=True)
    outdateOrder = models.DateTimeField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=False, default="N/A")
    cname = models.CharField(max_length=255, blank=False, default="N/A")
    phonecall = models.CharField(max_length=255, blank=False, default='0')
    datebook = models.DateTimeField(null=True, blank=False)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer} ({'Complete' if self.complete else 'Pending'})"

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
    image = models.ImageField(null=True, blank=True)

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
        ('seller', 'Chủ Khách Sạn'),
        ('customer', 'Khách Hàng'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, choices=ROLE_TYPE_CHOICES)
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)
    data_modified = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to="images/")

    def __str__(self):
        return self.user.username

    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url
    

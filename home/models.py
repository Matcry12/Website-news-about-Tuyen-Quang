from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# Create your models here.

#Change creaton form    
class CreationUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
class Product(models.Model):
    #productId = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    price = models.FloatField(max_length=255)
    quantity = models.IntegerField(max_length=255)
    onSale = models.BooleanField(default=False,null=False,blank=False)
    imageP = models.ImageField(null=True,blank=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    @property
    def imageURL(self):
        try:
            url = self.imageP.url
        except:
            url = ''
        return url    
class order(models.Model):
    #productId = models.ForeignKey(User, on_delete=models.CASCADE)
    _customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    dateOrder = models.DateTimeField(auto_now_add=True)
    outdateOrder = models.DateTimeField(null=True, blank=True)
    complete = models.BooleanField(default=False,null=False,blank=False)
    transactionId = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)
    @property
    def getCartItems(self):
        Cart = self.cart_set.all()
        total = sum([item.quantity for item in Cart])
        return total
    def getTotalPrice(self):
        Cart = self.cart_set.all()
        total = sum([item.getTotal for item in Cart])
        return total
class cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    Order = models.ForeignKey(order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0,null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True) 

    @property
    def getTotal(self):
        total = self.product.price * self.quantity
        return total

class new(models.Model):
    #productId = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    detail = models.CharField(max_length=2000)
    image = models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.title   
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
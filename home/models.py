from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class customer(models.Model):
    userName = models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10)
    email = models.CharField(max_length=200,null=True)
    phone = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.name
    
class product(models.Model):
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
    _customer = models.ForeignKey(customer, on_delete=models.SET_NULL, blank=True, null=True)
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
    Product = models.ForeignKey(product, on_delete=models.SET_NULL, blank=True, null=True)
    Order = models.ForeignKey(order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0,null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True) 

    @property
    def getTotal(self):
        total = self.Product.price * self.quantity
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
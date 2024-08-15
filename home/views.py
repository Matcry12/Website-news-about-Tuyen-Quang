from django.shortcuts import render
from django.http import HttpResponse
from .models import *

def get_firstHTML(request):
    news = new.objects.all()
    context = {'news': news}
    return render(request, 'apps/home.html', context)
def cart(request):
    context = {}
    return render(request, 'apps/cart.html', context)
def checkout(request):
    context = {}
    return render(request, 'apps/checkout.html', context)
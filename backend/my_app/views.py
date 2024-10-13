from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

# Create your views here.

def login(request):
    return HttpResponse("login")

def pageNotFound(request, exception):
    return  HttpResponseNotFound('<img src="https://avatars.mds.yandex.net/i?id=6327d4e69260d1c93797d2b806b31aa1_sr-9242319-images-thumbs&n=13"/>')
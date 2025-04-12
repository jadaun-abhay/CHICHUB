import base64

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render

# Create your views here.


def admin_login(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            response = {
                'error': True,
                'msg': 'Admin is not authenticated',
            }
            return JsonResponse(response, status= 403)
        response = {
            'error': False,
            'msg': 'Admin is authenticated',
        }
        return JsonResponse(response, status= 200)
    elif request.method == "POST":
        auth, credentials = tuple(request.META['HTTP_AUTHORIZATION'].split())
        if not auth == 'Basic':
            response = {
                'error': True,
                'msg': 'Invalid Basic Auth',
            }
            return JsonResponse(response, status= 403)
        credentials = base64.b64decode(credentials).decode('utf-8').split(':')
        credentials = {"username": credentials[0], "password": credentials[1]}
        username = credentials.get('username')
        password = credentials.get('password')
        queryset = User.objects.filter(username= username)
        if queryset.exists():
            user = authenticate(username=username, password= password)
            print(user)
            if user:
                auth_login(request, user)
                response = {
                    'error': False,
                    'msg': 'Admin login successful',
                }
                return JsonResponse(response, status= 200)
            response = {
                'error': True,
                'msg': 'Password is incorrect',
            }
            return JsonResponse(response, status= 401)
        response = {
            'error': True,
            'msg': 'Email does not exist',
        }
        return JsonResponse(response, status= 403)

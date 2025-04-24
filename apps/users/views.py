import base64
import re

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render

from apps.users.models import CustomUser
from apps.warehouse.enums import Status

from utils import common_regex as regex
from utils.functions import check_image_validity

# Create your views here.


def user_register(request):
    if request.method == 'POST':
        data = request.POST
        first_name = data.get('f_name').strip().upper()
        middle_name = data.get('m_name').strip().upper()
        last_name = data.get('l_name').strip().upper()
        email = data.get('email').strip()
        phone_number = data.get('phone_no').strip()
        password = data.get('password')
        confirm_password = data.get('c_password')
        profile_image = request.FILES.get('profile_img')
        
        if middle_name and not re.match(regex.NAME, middle_name):
            response = {
                'field': 'm_name',
                'msg': 'Fill a valid entry',
            }
            return JsonResponse(response, status= 400)
        if not re.match(regex.NAME, first_name):
            response = {
                'field': 'f_name',
                'msg': 'Fill a valid entry',
            }
            return JsonResponse(response, status= 400)
        if not re.match(regex.NAME, last_name):
            response = {
                'field': 'l_name',
                'msg': 'Fill a valid entry',
            }
            return JsonResponse(response, status= 400)
        if not re.match(regex.EMAIL, email):
            response = {
                'field': 'email',
                'msg': 'Fill a valid entry',
            }
            return JsonResponse(response, status= 400)
        if not re.match(regex.PHONE, phone_number):
            response = {
                'field': 'phone_no',
                'msg': 'Fill a valid entry',
            }
            return JsonResponse(response, status= 400)
        password = base64.b64decode(password).decode('utf-8')
        if not re.match(regex.PASSWORD, password):
            response = {
                'field': 'password',
                'msg': 'Fill a valid entry',
            }
            return JsonResponse(response, status= 400)
        confirm_password = base64.b64decode(confirm_password).decode('utf-8')
        if not password == confirm_password:
            response = {
                'field': 'c_password',
                'msg': 'Password is not matching',
            }
            return JsonResponse(response, status= 400)
        
        if profile_image:
            response = check_image_validity([profile_image])
            if not isinstance(response, bool):
                return JsonResponse(response, status= 400)
        
        user = CustomUser.objects.filter(email= email).exclude(status= Status.DELETED)
        if user:
            response = {
                'email': email,
                'msg': 'User already exists',
            }
            return JsonResponse(response, status= 400)
        user = CustomUser(first_name= first_name, middle_name= middle_name, last_name= last_name, email= email, phone_number= phone_number,)
        if profile_image:
            user.profile_image = profile_image
        user.set_password(password)
        user.save()
        response = {
            'msg': 'registration successful',
        }
        return JsonResponse(response, status= 201)


def user_login(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            response = {
                'msg': 'Not authenticated',
            }
            return JsonResponse(response, status= 401)
        response = {
            'msg': 'Authenticated',
        }
        return JsonResponse(response, status= 200)
    elif request.method == 'POST':
        auth, credentials = tuple(request.META['HTTP_AUTHORIZATION'].split())
        if not auth == 'Basic':
            response = {
                'msg': 'Invalid basic auth',
            }
            return JsonResponse(response, status= 200)
        credentials = base64.b64decode(credentials).decode('utf-8').split(':')
        credentials = {'email': credentials[0], 'password': credentials[1],}
        email = credentials.get('email')
        password = credentials.get('password')
        queryset = CustomUser.objects.filter(email= email)
        if queryset.exists():
            user = authenticate(email= email, password= password)
            if user:
                auth_login(request, user)
                response = {
                    'msg': 'Login successful',
                }
                return JsonResponse(response, status= 200)
            response = {
                'msg': 'Password is incorrect',
            }
            return JsonResponse(response, status= 400)
        response = {
            'msg': 'Email does not exists',
        }
        return JsonResponse(response, status= 409)
    else:
        response = {
            'msg': 'Method not allowed',
        }
        return JsonResponse(response, status= 405)


def user_logout(request):
    if request.method == 'POST':
        auth_logout(request)
        response = {
            'msg': 'Logout successful',
        }
        return JsonResponse(response, status= 200)
    else:
        response = {
            'msg': 'Method not allowed',
        }
        return JsonResponse(response, status= 405)
            

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
            user = authenticate(username= username, password= password)
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
    else:
        response = {
            'msg': 'Method not allowed',
        }
        return JsonResponse(response, status= 405)


def admin_logout(request):
    if request.method == 'POST':
        auth_logout(request)
        response = {
            'msg': 'Logout successful',
        }
        return JsonResponse(response, status= 200)
    else:
        response = {
            'msg': 'Method not allowed',
        }
        return JsonResponse(response, status= 405)

from django.http import JsonResponse


class LoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        paths = ['/auth/register/', '/auth/admin-portal/login/', '/auth/login/', '/', '/auth/']
        if request.user.is_authenticated or request.path in paths:
            response = self.get_response(request)
            return response
        else:
            response = {
                'msg': 'Unauthorized',
            }
            return JsonResponse(response, status= 401)

class AdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        admin_paths = ['/admin-portal/', '/admin-portal/category/management/',]
        if request.path in admin_paths:
            if request.user.is_superuser:
                response = self.get_response(request)
                return response
            else:
                response = {
                    'msg': 'Not authorized',
                }
                return JsonResponse(response, status= 403)
        else:
            response = self.get_response(request)
            return response

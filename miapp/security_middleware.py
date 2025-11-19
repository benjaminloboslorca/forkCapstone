# miapp/security_middleware.py
import logging
from django.http import HttpResponseForbidden
from django.core.exceptions import SuspiciousOperation

logger = logging.getLogger('django.security')


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://code.jquery.com https://stackpath.bootstrapcdn.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://stackpath.bootstrapcdn.com https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        response['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )
        
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response


class SuspiciousOperationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except SuspiciousOperation as e:
            logger.warning(
                f'Suspicious operation detected: {str(e)} '
                f'- IP: {self.get_client_ip(request)} '
                f'- Path: {request.path} '
                f'- Method: {request.method}'
            )
            return HttpResponseForbidden('Operación sospechosa detectada.')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SQLInjectionDetectionMiddleware:
    SQL_PATTERNS = [
        'union', 'select', 'insert', 'update', 'delete', 'drop',
        'create', 'alter', 'exec', 'execute', '--', '/*', '*/',
        'xp_', 'sp_', 'or 1=1', 'or 1 = 1', 'or true'
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        query_string = request.META.get('QUERY_STRING', '').lower()
        
        for pattern in self.SQL_PATTERNS:
            if pattern in query_string:
                logger.error(
                    f'SQL Injection attempt detected: {pattern} '
                    f'- IP: {self.get_client_ip(request)} '
                    f'- Path: {request.path} '
                    f'- Query: {query_string}'
                )
                return HttpResponseForbidden('Petición inválida.')
        
        if request.method == 'POST':
            for key, value in request.POST.items():
                value_str = str(value).lower()
                for pattern in self.SQL_PATTERNS:
                    if pattern in value_str:
                        logger.error(
                            f'SQL Injection attempt in POST data: {pattern} '
                            f'- IP: {self.get_client_ip(request)} '
                            f'- Field: {key}'
                        )
                        return HttpResponseForbidden('Datos inválidos.')
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
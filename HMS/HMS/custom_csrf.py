# custom_csrf.py

from django.middleware.csrf import CsrfViewMiddleware

class AllowAllCSRFOrigins(CsrfViewMiddleware):
    def _origin_verified(self, request):
        return True

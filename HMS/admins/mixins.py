from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

class OwnerRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an owner."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, 'role') or request.user.role != 'owner':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

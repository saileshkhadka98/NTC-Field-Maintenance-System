from rest_framework.permissions import SAFE_METHODS, BasePermission


def get_role(request):
    user = request.user
    if user and user.is_authenticated:
        return user.role
    return None


class IsAdminRole(BasePermission):
    """Admin only."""

    def has_permission(self, request, view):
        return get_role(request) == 'admin'


class AdminWriteElseRead(BasePermission):
    """Any logged-in user can read. Only admins can change data."""

    def has_permission(self, request, view):
        role = get_role(request)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return role == 'admin'


class StaffWriteElseRead(BasePermission):
    """Any logged-in user can read. Admins and technicians can change data."""

    def has_permission(self, request, view):
        role = get_role(request)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return role in ('admin', 'technician')


class StaffWriteAdminDelete(BasePermission):
    """Read: any logged-in user. Create/edit: admin or technician. Delete: admin."""

    def has_permission(self, request, view):
        role = get_role(request)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE':
            return role == 'admin'
        return role in ('admin', 'technician')


class StaffCreateAdminModify(BasePermission):
    """Read: any logged-in user. Create: admin or technician. Edit/delete: admin."""

    def has_permission(self, request, view):
        role = get_role(request)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return role in ('admin', 'technician')
        return role == 'admin'
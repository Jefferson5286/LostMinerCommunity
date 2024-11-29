from rest_framework.exceptions import PermissionDenied


class UnauthorizedOperation(PermissionDenied):
    default_detail = 'Not authorized to carry out the requested operation!'
    default_code = 'permission_denied'

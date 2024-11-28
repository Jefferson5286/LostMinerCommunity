from rest_framework.exceptions import PermissionDenied


class UnauthorizedContentOperation(PermissionDenied):
    default_detail = 'You are not allowed to perform the operation on the requested content.'
    default_code = 'permission_denied'

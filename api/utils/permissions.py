from api.utils.security import get_connection_from_token

from rest_framework import permissions
from rest_framework.request import Request


class IsAuthenticated(permissions.BasePermission):
    """
            Permissão personalizada que verifica a autenticação com base no token Bearer.
        O objeto 'connection' extraído do token será adicionado à request.
    """

    def has_permission(self, request: Request, view) -> bool:
        auth_header = request.headers.get('Authorization')
        print('Verify')

        if not auth_header or not auth_header.startswith('Bearer '):
            print('Bearer')
            return False

        # Remove o prefixo "Bearer " e obtém o token
        token = auth_header.split(" ", 1)[1]
        print(token)

        connection = get_connection_from_token(token)

        if not connection:
            print('Not connected')
            return False

        # Armazena a conexão na request para que a view possa acessá-la
        request.connection = connection
        print('Connected')
        return True

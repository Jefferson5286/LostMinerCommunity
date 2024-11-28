from api.utils.security import get_connection_from_token
from api.models import User, Content
from api.utils.exceptions import UnauthorizedContentOperation

from rest_framework import permissions
from rest_framework.request import Request


class IsAuthenticated(permissions.BasePermission):
    """
            Permissão personalizada que verifica a autenticação com base no token Bearer.
        O objeto 'connection' extraído do token será adicionado à request.
    """

    def has_permission(self, request: Request, view) -> bool:
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ', 1)[1]

        connection = get_connection_from_token(token)

        if not connection:
            return False

        request.connection = connection

        return True


class AuthorizeContentOperation(permissions.BasePermission):
    """
            Permissão para autorizar operações em conteúdo baseado no ID do usuário.

            Esta permissão garante que o usuário que faz a requisição (identificado por seu ID)
        tenha permissão para realizar a operação no conteúdo. A permissão só será concedida
        se o ID do usuário for igual ao `id` do conteúdo.
    """

    def has_permission(self, request: Request, view) -> bool:
        author_id: User = request.connection.user.id

        content: Content = Content.objects.get(id=request.parser_context['kwargs'].get('id'))

        if author_id != content.author.id:
            print('Não permitido')
            raise UnauthorizedContentOperation()

        return True

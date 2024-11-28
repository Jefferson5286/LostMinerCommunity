from rest_framework.response import Response

from api.models import Content
from api.utils.serializers import ContentSerializer
from api.utils.permissions import IsAuthenticated, AuthorizeContentOperation
from api.utils.pagination import ContentPagination
from api.utils.external_services import upload_image

from rest_framework.generics import (
    CreateAPIView, RetrieveAPIView, ListAPIView, DestroyAPIView, UpdateAPIView
)
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.views import APIView


class CreateContentView(CreateAPIView):
    """
    View para criar um novo conteúdo.

    Esta view permite que um usuário autenticado crie um novo conteúdo. O conteúdo
    será associado ao usuário que está fazendo a requisição.

    Permissões:
        - O usuário deve estar autenticado.

    A operação de criação é realizada pela `perform_create`, onde o autor do conteúdo
    é atribuído automaticamente com base no usuário autenticado.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ContentSerializer

    # noinspection PyUnresolvedReferences
    def perform_create(self, serializer: ContentSerializer):
        """
        Salva o conteúdo criado, associando o autor ao usuário autenticado.

        Args:
            serializer (ContentSerializer): O serializer que valida e salva os dados do conteúdo.
        """

        serializer.save(author=self.request.connection.user)


class GetContentView(RetrieveAPIView):
    """
    View para recuperar um conteúdo específico.

    Esta view permite que qualquer usuário obtenha detalhes de um conteúdo específico
    com base no seu ID.

    A resposta será o conteúdo serializado.

    Permissões:
        - Nenhuma permissão necessária, qualquer usuário pode visualizar o conteúdo.
    """
    serializer_class = ContentSerializer
    queryset = Content.objects.all()
    lookup_field = 'id'


class PaginationContentView(ListAPIView):
    """
    View para listar conteúdos com paginação.

    Esta view permite que os usuários vejam uma lista de conteúdos, com suporte para
    paginação e ordenação.

    Permissões:
        - O usuário deve estar autenticado.

    Ordenação:
        - Os conteúdos podem ser ordenados por `created_at` ou `name`.
    """
    serializer_class = ContentSerializer
    queryset = Content.objects.all()
    pagination_class = ContentPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ('created_at', 'name')
    ordering = ('created_at',)


class UpdateContentView(UpdateAPIView):
    """
    View para atualizar um conteúdo específico.

    Esta view permite que um usuário autenticado e autorizado atualize um conteúdo
    específico, desde que ele seja o autor do conteúdo.

    Permissões:
        - O usuário deve estar autenticado.
        - O usuário deve ser o autor do conteúdo.

    `perform_update` garante que o autor do conteúdo será o usuário autenticado.
    """
    permission_classes = [IsAuthenticated, AuthorizeContentOperation]
    queryset = Content.objects.all()
    lookup_field = 'id'
    serializer_class = ContentSerializer

    # noinspection PyUnresolvedReferences
    def perform_update(self, serializer: ContentSerializer):
        """
        Salva as alterações no conteúdo, associando o autor ao usuário autenticado.

        Args:
            serializer (ContentSerializer): O serializer que valida e salva os dados do conteúdo.
        """

        serializer.save(author=self.request.connection.user)


class DeleteContentView(DestroyAPIView):
    """
    View para excluir um conteúdo específico.

    Esta view permite que um usuário autenticado e autorizado exclua um conteúdo específico,
    desde que ele seja o autor do conteúdo.

    Permissões:
        - O usuário deve estar autenticado.
        - O usuário deve ser o autor do conteúdo.

    O conteúdo será deletado permanentemente da base de dados.
    """
    permission_classes = [IsAuthenticated, AuthorizeContentOperation]
    queryset = Content.objects.all()
    lookup_field = 'id'
    serializer_class = ContentSerializer


class UploadImagesView(APIView):
    """
    View para fazer upload de imagens para um conteúdo existente.

    Esta view permite que um usuário autenticado e autorizado faça o upload de imagens
    para um conteúdo específico. As imagens serão associadas ao conteúdo por URLs
    fornecidas por um serviço externo de armazenamento (ex: Cloudinary).

    Permissões:
        - O usuário deve estar autenticado.
        - O usuário deve ser o autor do conteúdo.

    O conteúdo será atualizado com os links das imagens armazenadas.
    """

    permission_classes = [IsAuthenticated, AuthorizeContentOperation]

    @staticmethod
    def post(request: Request, id: int):
        """
        Processa o upload das imagens e associa as URLs ao conteúdo.

        Args:
            request (Request): A requisição contendo as imagens a serem enviadas.
            id (int): O ID do conteúdo ao qual as imagens serão associadas.
            format (str, opcional): O formato de resposta (não utilizado neste exemplo).

        Returns:
            Response: Resposta com os dados do conteúdo atualizado (incluindo as URLs das imagens)
                      ou uma mensagem de erro se o conteúdo não for encontrado.
        """
        content: Content = Content.objects.get(id=id)

        if not content:
            return Response({'details': 'Content not found'}, 404)

        imagens = request.FILES

        for name, image in imagens.items():
            content.images_urls[name] = upload_image(image, 'contents')

        content.save()

        return Response(ContentSerializer(content).data, 200)

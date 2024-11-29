from api.utils.serializers import CommentSerializer, CommentEditSerializer
from api.models import Comment, Content
from api.utils.pagination import CommentPagination
from api.utils.permissions import IsAuthenticated, AuthorizeCommentOperation

from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


class ListCommentsView(ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    def get_queryset(self):
        return Comment.objects.filter(content=self.kwargs['content_id']).order_by('created_at')


class CreateCommentView(CreateAPIView):
    """
        Cria um comentário para um conteúdo específico.
        Pode responder a outro comentário, se o ID do comentário estiver no corpo da requisição.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: CommentSerializer):
        content_id = self.kwargs.get('content_id')

        try:
            content = Content.objects.get(id=content_id)

        except Content.DoesNotExist:
            raise NotFound({'detail': 'Content not found.'})

        answering_id = self.request.data.get('answering')
        answering_comment = None

        if answering_id:
            try:
                answering_comment = Comment.objects.get(id=answering_id, content=content)
            except Comment.DoesNotExist:
                raise NotFound({'detail': 'Answering comment not found in this content.'})

        serializer.save(
            author=self.request.connection.user,
            content=content,
            answering=answering_comment
        )


class UpdateCommentView(UpdateAPIView):
    """
        Atualiza o texto de um comentário específico.
    """

    serializer_class = CommentEditSerializer
    permission_classes = [IsAuthenticated, AuthorizeCommentOperation]
    queryset = Comment.objects.all()
    lookup_field = 'id'

    def partial_update(self, request, *args, **kwargs):
        # Verifica se apenas o campo `text` está sendo atualizado
        if list(request.data.keys()) != ['text']:
            return Response(
                {'detail': "Only the 'text' field can be updated."},
                status=400
            )

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = CommentSerializer(instance)

        return Response(response_serializer.data, status=200)


class DeleteComment(DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, AuthorizeCommentOperation]
    lookup_field = 'id'
    queryset = Comment.objects.all()

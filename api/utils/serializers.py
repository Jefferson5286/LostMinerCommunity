from api.models import Content, Comment

from rest_framework import serializers


def format_author(method):
    def wrapper(obj, *args, **kwargs):
        author = obj.author
        return {
            'user_id': author.id,
            'username': author.username,
        }
    return wrapper


class ContentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = '__all__'
        read_only_fields = ('created_at', 'id')

        extra_kwargs = {
            'images_urls': {'required': False},
            'description': {'required': False}
        }

    @staticmethod
    @format_author
    def get_author(obj: Content): ...

    def validate(self, attrs: dict) -> dict:
        if attrs.get('category') == 'world':
            return attrs

        elif attrs.get('category') in ('texture', 'skin'):
            if not attrs.get('resolution'):
                raise serializers.ValidationError("Resolution is required for this category.")

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    answering = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

        extra_kwargs = {
            'answering': {'required': False}
        }
        read_only_fields = ('created_at', 'id')

    @staticmethod
    @format_author
    def get_author(obj: Comment): ...

    @staticmethod
    def get_content(obj: Comment):
        """
            Retorna o ID do conteúdo associado ao comentário.
        """
        return obj.content.id

    @staticmethod
    def get_answering(obj: Comment):
        """
            Retorna os dados do comentário sendo respondido (se houver).
        """
        if obj.answering:
            return {
                'id': obj.answering.id,
                'author': {
                    'user_id': obj.answering.author.id,
                    'username': obj.answering.author.username,
                }
            }
        return None

class CommentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text',)

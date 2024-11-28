from api.models import Content

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


class CommentSerializer(serializers.Serializer):
    author = serializers.SerializerMethodField()

    @staticmethod
    @format_author
    def get_author(obj: Content):...

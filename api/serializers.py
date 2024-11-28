from api.models import Content

from rest_framework import serializers



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
    def get_author(obj: Content):
        return {
            'user_id': obj.author.id,
            'username': obj.author.username,
        }

    def validate(self, attrs: dict) -> dict:
        if attrs.get('category') == 'world':
            return attrs

        elif attrs.get('category') in ('texture', 'skin'):
            if not attrs.get('resolution'):
                raise serializers.ValidationError("Resolution is required for this category.")

        return attrs

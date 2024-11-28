from __future__ import annotations

from django.db.models import *


class Connection(Model):
    id = AutoField(primary_key=True)
    created_at = DateTimeField(auto_now_add=True)
    user = ForeignKey('api.User', on_delete=CASCADE)


class User(Model):
    id = AutoField(primary_key=True)
    username = CharField(unique=True, max_length=50)
    email = EmailField(unique=True)
    is_creator = BooleanField(default=False)

    password = TextField(null=True, blank=True)
    connections: QuerySet[Connection]

    def __str__(self):
        return self.username


class Comment(Model):
    id = AutoField(primary_key=True)
    content = ForeignKey('api.Content', on_delete=CASCADE, related_name='comments')
    created_at = DateTimeField(auto_now_add=True)
    author = ForeignKey('api.User', on_delete=PROTECT, related_name='comments')
    text = TextField()
    answering = ForeignKey('api.Comment', on_delete=CASCADE, blank=True, null=True, related_name='answers')

    answers: QuerySet[Comment]


class Content(Model):
    category_choices = (
        ('texture', 'Texture'),
        ('world', 'World'),
        ('skin', 'Skin')
    )

    id = AutoField(primary_key=True)
    name = CharField(max_length=50)
    description = TextField(blank=True, null=True)
    author = ForeignKey('api.User', on_delete=CASCADE)
    category = CharField(max_length=20, choices=category_choices)
    version = CharField(max_length=100)
    created_at = DateTimeField(auto_now_add=True)
    resolution = IntegerField(null=True, blank=True)
    download_url = URLField(unique=True)
    images_urls = JSONField(default=dict, blank=True)

    comments: QuerySet[Comment]

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'version'], name='unique_name_version')
        ]

    def __str__(self):
        return self.name


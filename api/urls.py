from django.urls import path
from api.views import auth, content


urlpatterns = [
    path('auth/authorize', auth.Authorize.as_view(), name='authorize'),
    path('auth/register', auth.Register.as_view(), name='register'),
    path('auth/login', auth.Login.as_view(), name='login'),
    path('auth/set_password', auth.SetPassword.as_view(), name='set_password'),
    path('auth/refresh_token', auth.RefreshToken.as_view(), name='refresh_token'),

    path('contents/create', content.CreateContentView.as_view(), name='create_content'),
    path('contents/details/<int:id>', content.GetContentView.as_view(), name='get_content'),
    path('contents/list/', content.PaginationContentView.as_view(), name='pagination'),
    path('contents/edit/<int:id>', content.UpdateContentView.as_view(), name='update_content'),
    path('contents/delete/<int:id>', content.DeleteContentView.as_view(), name='delete_content'),
    path('contents/upload_images/<int:id>', content.UploadImagesView.as_view(), name='upload_images'),
]
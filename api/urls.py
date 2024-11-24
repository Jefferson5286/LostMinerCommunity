from django.urls import path
from api.views import auth


urlpatterns = [
    path('authorize/', auth.Authorize.as_view(), name='authorize'),
    path('register/', auth.Register.as_view(), name='register'),
    path('login/', auth.Login.as_view(), name='login'),
    path('set_password/', auth.SetPassword.as_view(), name='set_password'),
    path('refresh_token/', auth.RefreshToken.as_view(), name='refresh_token'),
]
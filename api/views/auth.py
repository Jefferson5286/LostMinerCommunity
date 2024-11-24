from random import randint
from typing import Optional

from api.models import User, Connection
from api.utils.external_services import send_confirm_code
from api.utils.permissions import IsAuthenticated
from api.utils.validation import EMAIL_PATTERN
from api.utils.security import create_token, verify_password, hash_password

from django.http.response import JsonResponse as JSONResponse, HttpResponse as HTTPResponse
from rest_framework.request import Request
from rest_framework.views import APIView
from cachetools import TTLCache

auth_processing_cache = TTLCache(maxsize=5000, ttl=3600)


class Register(APIView):
    @staticmethod
    def post(request: Request) -> JSONResponse | HTTPResponse:
        """
        Registra um novo usuário, validando a presença e o tipo dos campos no corpo da requisição,
        além de verificar se o e-mail já está em uso. Caso alguma validação falhe, retorna um erro
        apropriado. Se todas as validações passarem, envia um código de confirmação para o email
        do usuário e armazena temporariamente os dados para a operação de registro.

        Parâmetros:
            request (Request): A requisição HTTP que contém os dados para o registro.

        Retorna:
            JSONResponse | HTTPResponse: retorna uma resposta JSON com uma mensagem de erro em caso
            de falha, ou uma resposta HTTP com código 201 em caso de sucesso.
        """

        # Verificando se os campos 'username' e 'email' estão presentes na requisição.
        if not all(field in request.data for field in ['username', 'email']):
            return JSONResponse(
                data={'message': 'Both <username> and <email> are required.'},
                status=400
            )

        # Verificando se todos os campos presentes na requisição são do tipo string.
        if any([not isinstance(item, str) for item in request.data.values()]):
            return JSONResponse(
                data={'message': 'Some of the fields have the wrong type. Only <string> accepted!'},
                status=422
            )

        if not EMAIL_PATTERN.match(request.data['email']):
            return JSONResponse(
                data={'message': 'Incorrect email format.'},
                status=422
            )

        # Verificando se o e-mail fornecido já existe no banco de dados.
        if User.objects.filter(email=request.data['email']).exists():
            return JSONResponse(
                data={'message': 'Email already exists.'},
                status=409
            )

        confirm_code = ''.join([str(randint(0, 9)) for _ in range(0, 6)])

        # Armazenando os dados temporariamente no cache para o processo de verificação posterior.
        # O código de confirmação será usado para autorizar o registro.
        auth_processing_cache[confirm_code] = {
            'username': request.data['username'],
            'email': request.data['email'],
            'operation': 'register'
        }

        send_confirm_code(request.data['email'], request.data['username'], confirm_code)

        return HTTPResponse(status=201)


class Authorize(APIView):
    @staticmethod
    def post(request: Request) -> JSONResponse | HTTPResponse:
        """
        Processa uma solicitação de autorização com base em um código fornecido no corpo da requisição.
        Verifica o tipo e a presença do campo <code>, realiza a operação correspondente
        (registro ou login) e retorna um token de autenticação.

        Parâmetros:
            request (Request): A requisição HTTP contendo o campo <code>.

        Retorna:
            JSONResponse: Resposta JSON com o token em caso de sucesso ou mensagem de erro em caso de falha.
        """

        code = request.data.get('code')

        if code is None:
            return JSONResponse({'message': 'Field <code> is required.'}, status=400)

        if not isinstance(code, str):
            return JSONResponse(
                {'message': f'Incorrect type for <code>. Expected <string>, received {type(code).__name__}.'},
                status=422
            )

        # Verificação do código no cache
        data: Optional[dict] = auth_processing_cache.get(code)

        if data is None:
            return JSONResponse({'message': 'Unauthorized!'}, status=401)

        # Processamento baseado na operação (registro ou login)
        match data.get('operation'):
            case 'register':
                user = User.objects.create(email=data['email'], username=data['username'])

            case 'login':
                user = User.objects.filter(email=data['email']).first()
                if not user:
                    return JSONResponse({'message': 'Unauthorized!'}, status=401)

            case 'password':
                user = User.objects.filter(id=data['user_id']).first()
                user.password = hash_password(data['password'])

                user.save()

                return HTTPResponse(status=201)

            case _:
                return JSONResponse({'message': 'Unauthorized!'}, status=401)

        connection = Connection.objects.create(user=user)

        token = create_token(connection.id)

        return JSONResponse({'token': token}, status=200)


class Login(APIView):
    @staticmethod
    def post(request: Request) -> JSONResponse | HTTPResponse:
        """
            Realiza o login do usuário, verificando o e-mail e a senha. Se as credenciais
            forem válidas, um token JWT é retornado. Caso contrário, envia um código de
            confirmação para o e-mail do usuário.
        """

        # Verificando se o campo 'email' está presente na requisição.
        if 'email' not in request.data:
            return JSONResponse({'message': 'Missing <email>.'}, status=400)

        # Verificando se todos os campos presentes na requisição são do tipo string.
        elif any([not isinstance(item, str) for item in request.data.values()]):
            return JSONResponse(
                data={'message': 'Some of the fields have the wrong type. Only <string> accepted!'},
                status=422
            )

        # Verificando se o formato do e-mail está correto.
        elif not EMAIL_PATTERN.match(request.data['email']):
            return JSONResponse(
                data={'message': 'Incorrect email format.'},
                status=422
            )

        try:
            user = User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            return JSONResponse({'message': 'User not found.'}, status=404)

        if request.data.get('password'):
            if not verify_password(request.data['password'], user.password):
                return JSONResponse({'message': 'Incorrect password.'}, status=401)

            connection = Connection.objects.create(user=user)

            return JSONResponse({'token': create_token(connection.id)}, status=200)

        confirm_code = ''.join([str(randint(0, 9)) for _ in range(0, 6)])

        auth_processing_cache[confirm_code] = {
            'email': request.data['email'],
            'operation': 'login'
        }

        send_confirm_code(user.email, user.username, confirm_code)

        return HTTPResponse(status=201)


class SetPassword(APIView):
    """
    API endpoint para iniciar o processo de redefinição de senha.
    Envia um código de confirmação para o email do usuário e armazena os dados temporariamente no cache.
    """
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def put(request: Request) -> JSONResponse | HTTPResponse:

        # Verificar se o campo 'password' está presente
        if 'password' not in request.data:
            return JSONResponse(
                data={'message': 'Field <password> is required.'},
                status=400
            )

        # Verificar se o campo 'password' é uma string válida
        if not isinstance(request.data['password'], str) or not request.data['password'].strip():
            return JSONResponse(
                data={'message': 'Invalid type for <password>. Expected a non-empty string.'},
                status=422
            )

        user = request.connection.user

        confirm_code = ''.join([str(randint(0, 9)) for _ in range(6)])

        auth_processing_cache[confirm_code] = {
            'user_id': user.id,
            'password': request.data['password'],
            'operation': 'password'
        }

        send_confirm_code(user.email, user.username, confirm_code)

        return HTTPResponse(status=201)


class RefreshToken(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def put(request: Request) -> JSONResponse | HTTPResponse:
        connection = request.connection

        new_connection = Connection(user=connection.user)
        new_connection.save()

        connection.delete()

        return JSONResponse({'token': create_token(new_connection.id)}, status=200)

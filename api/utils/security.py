from datetime import timedelta
from typing import Optional

from LostMinerCommunity import settings
from api.models import Connection

from django.utils.timezone import now
from jose import jwt, JWTError
from bcrypt import checkpw, hashpw, gensalt


def create_token(connection: int) -> str:
    payload = {'con': connection}

    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def get_connection_from_token(token: str) -> Optional[Connection]:
    """
        Recupera uma instância de conexão associada a um token JWT.

        Esta função decodifica o token JWT usando a chave secreta configurada em `settings.SECRET_KEY` e verifica
        se o token contém um ID de conexão válido. Se a conexão associada ao ID não existir ou se a data de criação
        da conexão for maior que 1 dia atrás, a função retornará `None`. Caso contrário, retornará a instância de
        `Connection`.

        Parâmetros:
            token (str): O token JWT que contém o ID da conexão no seu payload.

        Retorna:
            Optional[Connection]: A instância da conexão associada ao token, ou `None` se o token for inválido,
            não contiver um ID de conexão, ou a conexão for inválida.

        Exceções:
            JWTError: Se houver erro ao tentar decodificar o token JWT, a função retorna `None`.

        Exemplo:
            connection = get_connection_from_token('seu_token_aqui')
            if connection:
                # Faça algo com a conexão
            else:
                # Token inválido ou conexão expirada
        """
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        # Obtém o ID da conexão do payload
        connection_id = data.get('con')

        if not connection_id:
            print('not id')
            return None

        connection = Connection.objects.filter(id=connection_id).first()

        # Verifica se a conexão existe e se não expirou
        if connection:
            if connection.created_at + timedelta(days=1) >= now():
                return connection

            connection.delete()
            return None

        print('expires')

    except JWTError:
        print('jwt error')

    return None


def hash_password(password: str) -> str:
    salt = gensalt()
    hashed = hashpw(password.encode('utf-8'), salt)

    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomUser:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.is_authenticated = True

    def __repr__(self):
        return f"<CustomUser id={self.id}, username={self.username}>"


class CustomJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        from .views import dynamodb # Importar o dynamodb

        role = user_id = validated_token.get("role")
        if role == "cliente":
            table = "utilizadores"
        else:
            table = "funcionarios"

        user_data = dynamodb.scan(TableName=table)
        user_data = user_data['Items']
        ids = [int(user_data[i]['id']['N']) for i in range(len(user_data))] # id de todos os utilizadores

        user_id = validated_token.get("user_id")
        
        if not user_id or user_id not in ids:
            raise AuthenticationFailed("Utilizador não encontrado.")
        
        return CustomUser(user_id, validated_token.get("username"))

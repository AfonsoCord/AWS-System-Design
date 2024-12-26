from rest_framework import status
from .serializers import LoginSerializer, LoanSerializer, BankLoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import emprestimo
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import boto3
from rest_framework.response import Response
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser


bucket_name = 'bankingsystem'
collection_name = 'faces' # ficou guardado no regnonition não no s3

aws_access_key_id="ASIAYS2NSE42JUZEJMYN"
aws_secret_access_key="3WBKTmxbKqGRINw6SO2MVkz5zm4jwTRCAw4Abxdz"
aws_session_token="IQoJb3JpZ2luX2VjEF0aCXVzLXdlc3QtMiJIMEYCIQCVmw1F/1USh8LcSx1d3VziHVqrvbv2JXHM/OG9CCuQhQIhAPLjOW36MGO2qmKdAEchKz1RYu+Z5MSRRtwQ1J2o/hqzKrQCCDYQABoMNTkwMTgzODAyNjc2Igy5cI4AOGmSoAvVvJsqkQKBWl1epElPpCHEoGKyFOi6soGganZ1QuM5DBP5AHdnRs9p5Bh/l05jplK//K/M1tHH1JAcvHbm6oBKJbHMgETEJJLgRWtX6Lgeq4N6kvK197Md4rkriCOFpw/EzzAZYmjgSzcWr7Fiju0UjiBPiwFAoL7NddSYm5FO88fZVyGo7D7Z3plXrj/H3F1iZYIi24nMy9WxWCCnrgtbQ8L4xIdcBs0U0vHwNvBHm0ftl+yXwMu9vxyX57T5PXRqwAbhYh+Nu3GtlquSkKTt/ArrvNgG7hmDyegGkSYrEXFr5A3Zz1TXJEcAX1BOt86EKcDFkjnp5u5mNmCPpDzcGtQtdUe8j/DNZIKQ0p1m/T9h/AFtJbwwz/62uwY6nAEbYF1+ZNIktHfcQxMIafsWKqGHl/Fs87Fx/hb07pVPXIiIU+B+pviCPyBXzFj2OnsHeaQ5p4k3HRYsMz5LinG/P2eQPz2jOGGGVIohjc6XzqH0VBRx7SK9JIXAUYZ7vCixaD/7b+TZwSuhmG4i08YukYJWcZOSa4C7zLXRVBEVLIGvckIIlZ+8/F6YMVjq6Ysf7YkUrC6CKqzfdwo="
boto3.setup_default_session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token,
    region_name='us-east-1'
)

s3 = boto3.resource('s3',
                    aws_access_key_id = aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token
                    )

client = boto3.client('rekognition',
                region_name = 'us-east-1',
                aws_access_key_id = aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token
                )

dynamodb = boto3.client('dynamodb',
                region_name = 'us-east-1',
                aws_access_key_id = aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token
                )

my_bucket = s3.Bucket(bucket_name)   


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request): 
    serializer = LoginSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    try:
        response = client.search_faces_by_image(
            CollectionId=collection_name,
            Image={'Bytes': request.FILES['photo'].read()},
            MaxFaces=5,
            FaceMatchThreshold=90)
        
        id_cara = response["FaceMatches"][0]["Face"]["FaceId"]

    except:
        return Response({"message": "O reconhecimento facial falhou."}, status=status.HTTP_400_BAD_REQUEST)
    
    user = dynamodb.query(TableName="utilizadores", KeyConditionExpression="faceid = :id", ExpressionAttributeValues={':id':{'S':id_cara}})

    if user['Items'] != []:

        # Criar tokens
        refresh = RefreshToken()
        refresh["user_id"] = int(user['Items'][0]['id']['N'])
        refresh["username"] = user['Items'][0]['username']['S']
        refresh["role"] = "cliente"

        access = refresh.access_token
        access["user_id"] = int(user['Items'][0]['id']['N'])
        access["username"] = user['Items'][0]['username']['S']
        access["role"] = "cliente"


        return Response({
            'message': 'Login successful',
            'access_token': str(access),
            'refresh_token': str(refresh),
            'username': user['Items'][0]['username']['S'],
            'valid': '1'
        })
    else:
        return Response({'message': 'Utilizador não reconhecido', 'valid': '0'}, status=401)
    


@api_view(['POST'])
@permission_classes([AllowAny])
def loan_simulator(request):
    if request.method == 'POST':
        serializer = LoanSerializer(data=request.data)

        if serializer.is_valid():
            return Response("Parabéns!", status=status.HTTP_200_OK)
        else:
            return Response("Erro na simulação.", status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Home(request):
    serializer = LoanSerializer(data=request.data)

    if serializer.is_valid():

        emprest = emprestimo(
            user = serializer.validated_data['user'],
            valor = serializer.validated_data['valor'],
            duracao = serializer.validated_data['duracao'],
            salario = serializer.validated_data.get('salario'),
            profissao = serializer.validated_data.get('profissao'),
            documentos = serializer.validated_data.get('documentos'),
            tiposempr = serializer.validated_data.get('tiposempr'),
            estado = serializer.validated_data.get('estado'))
        emprest.save()

        return Response("Parabéns!",status=status.HTTP_200_OK)
    
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def BankLogin(request):
    serializer = BankLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = request.data['username']
    password = request.data['password']

    user = dynamodb.query(
        TableName="funcionarios",
        KeyConditionExpression="username = :username",
        FilterExpression='password = :password',
        ExpressionAttributeValues={':username':{'S': username}, ':password': {'S': password}}
    )
    
    # Criar tokens
    if user['Items'] != []:

        refresh = RefreshToken()
        refresh["user_id"] = int(user['Items'][0]['id']['N'])
        refresh["username"] = user['Items'][0]['username']['S']
        refresh["role"] = "staff"

        access = refresh.access_token
        access["user_id"] = int(user['Items'][0]['id']['N'])
        access["username"] = user['Items'][0]['username']['S']
        access["role"] = "staff"

        return Response({
            'message': 'Login successful',
            'access_token': str(access),
            'refresh_token': str(refresh),
            'username': user['Items'][0]['username']['S'],
            'valid': '1'
        })
    else:
        return Response({'message': 'Invalid username or password', 'valid': '0'}, status=401)

    

# estado do empréstimo
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loan_status(request):
     
    username = request.GET.get('username')

    if not username:
            return Response({"message": "O campo 'username' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    emprestimos = emprestimo.objects.filter(user=username)
    print(emprestimos)

    if not emprestimos.exists():
        return Response({"message": "Não foram encontrados empréstimos para este utilizador."}, status=status.HTTP_404_NOT_FOUND)

    emprestimo_data = [
        {
            "valor": emprest.valor,
            "duracao": emprest.duracao,
            "salario": emprest.salario,
            "profissao" : emprest.profissao,
            "tiposempr": emprest.tiposempr,  
            "tempo": emprest.tempo, 
            "estado": emprest.estado,
        }
        for emprest in emprestimos
    ]

    return Response({
        "message": f"Você possui {len(emprestimo_data)} empréstimo(s) em processamento.","emprestimos": emprestimo_data}, status=status.HTTP_200_OK)


# acesso ao estado de todos os empréstimos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loan_status_funcionarios(request):
    emprestimos = emprestimo.objects.all()

    if not emprestimos:
        return Response({"message": "Não foram encontrados empréstimos de clientes."}, status=status.HTTP_404_NOT_FOUND)

    emprestimo_data = [
        {
            "cliente": emprest.user,  
            "valor": emprest.valor,
            "duracao": emprest.duracao,
            "salario": emprest.salario,
            "profissao": emprest.profissao,
            "tiposempr": emprest.tiposempr,  
            "estado": emprest.estado,
        }
        for emprest in emprestimos
    ]

    return Response({
        "message": f"Existe(m) {len(emprestimo_data)} empréstimo(s) registado(s) no sistema.", "emprestimos": emprestimo_data},
        status=status.HTTP_200_OK)


# atualizar o estado e a decisão do emprestimo dos clientes
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def status_decision(request, id):
    try:
        emprestimo = emprestimo.objects.filter(id=id)

        if emprestimo.exists():
           
            estado = request.data.get('estado')
            decisao = request.data.get('decisao')

            # atualiza o estado e a decisao diretamente na bd
            emprestimo.update(estado=estado, decisao=decisao)

            return Response({"message": "Empréstimo atualizado com sucesso."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Empréstimo não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
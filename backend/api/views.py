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

aws_access_key_id="ASIAYS2NSE42JQRGOCEY"
aws_secret_access_key="veUgGzNJ38oLdcO0JQlos+KoF+GlKF49myZoAEgt"
aws_session_token="IQoJb3JpZ2luX2VjEFkaCXVzLXdlc3QtMiJHMEUCIGLyilRiU9+jnEZ/GX9xdIwhYrabERorVG88gB11IWJqAiEAxfvjY8K5Kd7XG9n0ibmsnGJPNACf99HanwssAC/j/B4qtAIIMhAAGgw1OTAxODM4MDI2NzYiDLZEhgOGPs7v6ml4CSqRAtYXVDvvmVzcrBnvRTgXJOlpOouRqM8QRGyzK9iyPIRPvm5rZ+h/Nv5XsQm4J67UUjirbDLVVQoMkSuXKDJkul6FnN/ZpP03gxHIgp6fiQKQL7wBJQB8YXp7fM7wGiLJXquzyhb/LlPovEsbrqoZrOGykMlBZeak2ikiAsd/bngmxal7e4YL4H4WxhsSTxc34LyMFc2tx0e6Z+2vBNiHqpjnKEHpY5gVAf2bxxR0LhomF5xg6Wt7+SqT+QfNBDBirmYO6pEiE72XrIXZgUcrl2lGsgM7NNe8J/dMpkzIKYbsLaQynGQ5JVe+g4canaK1na5sD+dPYmpyAv8M/mZtIhngwoiKgvyqaU9F4LrzNupIdDCthba7BjqdAXoz92SwzVhRdm9HPUCQNH6DMxbKy8pRHc9U9oUtS2ftiYmYglOaKz0XPqUUV1WVUqj5YU3ufEnTYtGHvdb+0V0l9JUdreUO8TzVeofi24fK0sQUiPPMXfSEMz/YLhfNzv/tpQk111xJHOG70xz8E0t+FdmGWeQuhrChEIBwrpdsEF9P1FBB0xEBUv9eFzshJmemkfpf27HFpCPLrmY="
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

        access = refresh.access_token
        access["user_id"] = int(user['Items'][0]['id']['N'])
        access["username"] = user['Items'][0]['username']['S']


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

    #data = emprestimo.objects.create()
    
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

        access = refresh.access_token
        access["user_id"] = int(user['Items'][0]['id']['N'])
        access["username"] = user['Items'][0]['username']['N']

        return Response({
            'message': 'Login successful',
            'access_token': str(access),
            'refresh_token': str(refresh),
            'username': username,
            'valid': '1'
        })
    else:
        return Response({'message': 'Invalid username or password', 'valid': '0'}, status=401)

    

# estado do empréstimo
@api_view(['GET'])
@permission_classes([AllowAny])
def loan_status(request):
     
    username = request.GET.get('username')

    if not username:
            return Response({"message": "O campo 'username' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    emprestimos = emprestimo.objects.filter(user=username)

    if not emprestimos.exists():
        return Response({"message": "Não foram encontrados empréstimos para este utilizador."}, status=status.HTTP_404_NOT_FOUND)

    emprestimo_data = [
        {
            "valor": emprest.valor,
            "duracao": emprest.duracao,
            "salario": emprest.salario,
            "profissao" : emprest.profissao,
            #"documentos": emprest.documentos,
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
@permission_classes([IsAdminUser])
def loan_status_funcionarios(request):
    emprestimos = emprestimo.objects.all()

    if not emprestimos:
        return Response({"message": "Não foram encontrados empréstimos de clientes."}, status=status.HTTP_404_NOT_FOUND)

    emprestimo_data = [
        {
            "usuario": emprest.user.username,  
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
        "message": f"Existem {len(emprestimo_data)} empréstimo(s) registados no sistema.", "emprestimos": emprestimo_data}, status=status.HTTP_200_OK)

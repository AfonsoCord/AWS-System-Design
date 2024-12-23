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


bucket_name = 'bankingsystem'
collection_name = 'faces' # ficou guardado no regnonition não no s3

aws_access_key_id="ASIAYS2NSE42OIHG2TF2"
aws_secret_access_key="t/x/aBkT4V3u3hCXmutlcCM7rbNpIsD22c/9solO"
aws_session_token="IQoJb3JpZ2luX2VjEAwaCXVzLXdlc3QtMiJHMEUCIQDZIU6xX+7s58SxqGnheQdpEQjGwBOnQomQmZAA2WA4wAIgGaunFUsG7FVnzzw6om2A/ye4xnpTX8d5d463LU8i4BgqvQII1f//////////ARAAGgw1OTAxODM4MDI2NzYiDKPN69hRDqHywuE0ySqRAsMc7MwD1Qi4zTB4us8FufYp2sKT+NMzEgP1gg87dfDfsmomuR51QbDMztTWkNTcakGpNmqEOAE5gVawvEwIxgodEPKC4Re+cd2t47ZQOYO/849zHR3izVxwsX3MRGXrNyuSiGirGy5g9OeruufFNzgCrWeBSzGCaHeb6QXHRDn3vCQWZFxWvSCeuQq04k9cXEwnBwmVmnXVmxVmMmLwrkqT6SMBZF7deF6nJwbOEGPRxZLJaVVpFatg2li4hiW1uNyta8Rxz8Rm6/ZmpQoqc1vFRmRLELBgiI5Qt4hD/NNnHsr7TwNi5ljpRqDQpULXcPv5ecdd0x/twgff6/in8I60ypysRDqpqCkrF8wEaAoC4zDMmKW7BjqdAXhYX376la6g8xO8T4VUYvEistv207hXSSC4Z2vdVN67FupSNlzLs4/UWwXKahs8u+unw0nACf/+oOLd0POW56UUvPnFsrkNrF1WzcolY7LkpgVYzcD6NBWV2DBmh5sCkfB3P3HTWmLvBbBK0Fbc6amV9TKVOaovedYs5BSF6oQLjU7kqN5ETqRm2m28ntixqE1lBZXaGPIG+JgqgYI="

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

    user = dynamodb.query(TableName="funcionarios",
                          KeyConditionExpression="username = :username",
                          FilterExpression='password = :password',
                          ExpressionAttributeValues={':username':{'S': username}, ':password': {'S': password}})
    
    if user['Items'] == []:
        return Response({"message": "O login falhou."}, status=status.HTTP_400_BAD_REQUEST)
        
    if user is not None:
        refresh = RefreshToken()
        refresh["user_id"] = user['Items'][0]['username']['S'] # ainda tem que se mudar isto

        access = refresh.access_token
        access["user_id"] = user['Items'][0]['username']['S']

        return Response({
            'message': 'Login successful',
            'access_token': str(access),
            'refresh_token': str(refresh),
            'username': user['Items'][0]['username']['S'],
            'valid': '1'
        })
    else:
        return Response({'message': 'Invalid email or password', 'valid': '0'}, status=401)
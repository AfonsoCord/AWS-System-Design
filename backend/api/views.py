from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics,status,permissions
from .serializers import LoginSerializer, LoanSerializer, BankLoginSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import emprestimo
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import boto3
from django.db import models
from rest_framework.response import Response
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import permission_classes


bucket_name = 'bankingsystem'
collection_name = 'faces' # ficou guardado no regnonition não no s3

aws_access_key_id="ASIAYS2NSE42NASWUQZZ"
aws_secret_access_key="cvvdXLk0n2mFSCl+IxUdm+Ud38sRW7eQMaCqkzB6"
aws_session_token="IQoJb3JpZ2luX2VjEOT//////////wEaCXVzLXdlc3QtMiJIMEYCIQD0tfVDdSbPMR48r/T3w9q0YTItZfd3ZIisUIJ1ocHscwIhAIjxjPrFOZVH63qZCZCifyenkHMI1e8t7JManKRPdeILKr0CCK3//////////wEQABoMNTkwMTgzODAyNjc2IgyeQCtX6VflCA4b/2MqkQJt+ZJvFnRKlmGe29ervj06v8sGvJtKTVnc0Ma512SGxKXGCJFg9VmyVG9R9MsBM/jmVLXCqHUZ680mTN85PN8Mp2wCH3L4qP0jY26BRkI7L+f0qCFhwZYN3JSrrxnPz8pKPjFGXGO37B2KsFivLAIMea0bEp49p4uqlm9BgiU3aR592UWgqepm5ZYFcNdRfKXyWXjB6jc2sDfZ2PVVpgyu5TKAWHDv3bGO+KNK6wI7Ib5j2JXPygBfIzdeiZTW5cHRuaIY+feuyNwNQEMjtZC5ZZyCldpY3DpMzLUmlsQSLkHfeJ7g2zWo/mEOxu0Nb5pN19B5DL4ZYgtVwLQiGoEEnUb5jkz9w41PT848QNhtQcUw27ucuwY6nAGxy+R3g2+P8kvUIK2O1W9oJb5vMNrfZoh0uz6nTbEYej7/KXOKIE3k7uKzo3yoC7xyat74HSw6SUZh9bew9A8pJ68iLJHZb89LfyPKgJBkYGxcYwir7f3lXQxYX1bM7MVsPRpZrohehYqE9PbrDN6xjGXjVZCn9ZXo/m0dGr4yYMfBPckkcVhddpYbRdCDal6Vs58pI1WMSdMqtrE="

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
    
    data = {
            "CollectionId": "bankingsystem",
            "Image": {}}

    
    #A pesquisa ja funciona so falta ser na web que se mete a foto

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
        refresh = RefreshToken()
        refresh["user_id"] = user['Items'][0]['id']['N']
        refresh["type"] = "refresh"
        access = refresh.access_token
        access["user_id"] = user['Items'][0]['id']['N']


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
        request_data = request.data.copy()
        request_data['person'] = request.user.username

        if request_data:
            return Response("Parabéns!",status=status.HTTP_200_OK)
        else:
            return Response("erro", status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
def Home(request):
    print("==========================================================")
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
        refresh["user_id"] = user['Items'][0]['username']['S']
        refresh["type"] = "refresh"

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
   
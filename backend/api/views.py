from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics,status,permissions
from .serializers import  Simulador,LoginSerializer, LoanSerializer, BankLoginSerializer
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

aws_access_key_id="ASIAYS2NSE42DKPK2WPK"
aws_secret_access_key="3K2KhERV9YzHh714Xh8kvJd7oSevLO2RkX/orloA"
aws_session_token="IQoJb3JpZ2luX2VjEMT//////////wEaCXVzLXdlc3QtMiJIMEYCIQC2o+h6ZergJcjEu3wZPTnuvZ0tiwNqqvJeJX5lm+WVAgIhAIEziTTaQGIsSkXsHv0DASzywfrVohYf70ARqLlJAKjVKr0CCI3//////////wEQABoMNTkwMTgzODAyNjc2IgzdqqAN/BG36OV4HCUqkQK2iZlKVxm8OPtcM4IqSjbgPodxxiO+3lYGdVeaptZfv+qQbq37CRbPaUdXvxV5snPD4xEwRI/MbvkB0Koi8ztnzJNPXPNC4RriEb0WPeEja44kPbRBuiX5HHOc6zgLxYou77th3xEIZBUloQ3BpOLwv0HUih2b25gLLFxohD1qAnZNp9B0oeUQ9gE+b01P6oA2IiW5zu8CuZ7NbSQohg8MltZjmk7cDwitIU5Zd/24WHiumYKBor2deil2z2XBIusIB/3Qs3kTH5+qgFVlPqT+yzvTKZwu5XlTaJSLnihkhuewvmgwDykiR4D2L4vJdLlTdH3Tn1omlGMWzs4n4upZbCD47H/wZjQdR+jl0GRMgWQwzMCVuwY6nAG3PpmXg4KjjDehwice3zFSoynIAcwJ1CZ/0f83lNiVDahe6I0V8wCSft9f8Nx/JV/cdtB8zk+3UTC6YLW5dgtnw+Ge3nc/oJHdGJTYxnjPCsF7Fmu9kh+IZ/L7wKPcQXcZXGa3ehxfrcVS244UM1cKAiUb7FZdLucAx3y+p4uoyjr/ioh/SwMF6GO2HYRP2dw5TOzpGsw/xhhUXrc="

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

    #user = emprestimo.objects.get(id_cara=id_cara)
    user = dynamodb.query(TableName="utilizadores", KeyConditionExpression="faceid = :id", ExpressionAttributeValues={':id':{'S':id_cara}})
    if user['Items'] != []:
        refresh = RefreshToken()
        refresh["user_id"] = user['Items'][0]['faceid']['S']
        refresh["type"] = "refresh"

        access = refresh.access_token
        access["user_id"] = user['Items'][0]['faceid']['S']

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
            loan = serializer.save(valor = request.data["valor"],
                            duracao= request.data["duracao"])
            
            return Response("Parabéns!",status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
def Home(request):
    loan = emprestimo.objects.get(valor=12412)
    serializer = LoanSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(request.data)

    emprest = emprestimo()
    emprest.valor = request.data['valor']
    emprest.duracao = request.data['duracao']
    emprest.salario = request.data['salario']
    emprest.profissao = request.data['profissao']
    emprest.documentos = request.data['documentos']
    emprest.tiposempr = request.data['tiposempr']
    emprest.estado = request.data['estado']
    emprest.save()


    data = emprestimo.objects.create()

    return Response("Parabéns!",status=status.HTTP_200_OK)





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
   
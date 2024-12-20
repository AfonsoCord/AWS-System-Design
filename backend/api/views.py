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

aws_access_key_id="ASIAYS2NSE42FNDRTMME"
aws_secret_access_key="DGrtAQeT1JuIOEARMxjdHPR7qK5zzdGVxfyTNrAm"
aws_session_token="IQoJb3JpZ2luX2VjELn//////////wEaCXVzLXdlc3QtMiJHMEUCIA8wvjVCOitRv6R10+zAtR3PSudtVJRri3x/pehORE6DAiEA66kfYITQ/VxtzhJaV19eVNEv5eQKwehZGt3mSHc4jYIqvQIIgv//////////ARAAGgw1OTAxODM4MDI2NzYiDEAeutP8WNFKASlQDiqRAru/bU8uBt/9MoYNbMBc6W3atUCJliVtKcufqOFqP39Uofy0//E9T3xd1QDLvnZanVgAzlEVf63GPBEvg4DoR8vO38Rx5tciJt0YVZ1J8MsMzizQ6lS3qiN5R4AWqFdwjDSbgR8fOZtUIouX0hVKBX607NcMHfPmDIVgrYxFCC8G0QDHns+yGhfYlWCYZTYY1+82KzKz2WY09rf4rkRjrSn2UNELBhxooLZNZjwYhT6h5cx/1xx17PO+z4fpRf+eljXBx3AbfkVtY+ORjCgY0rsX5L3exhKTo9U/Svfe/+v5WCzrA4j3rS178XkuZywU/1U9dUX6lS+a5rI8KK0JMncHG05Kky4+Ygn2o5FyufsIHzCn85K7BjqdAZrPHoK3ZkxX7VkIr57m2+tzBmJqTKCZVOxJQvM1Q9uclyp9s59iYOrg5+qXlZk0AI9m0raMQ51NH5njb/Cfkfv/W3rA2NcPtSQuyT8PwA8IgnivPbaMgJIkYNgDhA088KiX3neQYSH7WNsWeixYuV7/zS6YyuCBVyJKPWFfQUuHIAtBPPvA6f1MVDxvq4MORoJef1BO4IOVUj44Sa4="

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
            return Response("Parabéns!",status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
def Home(request):
    print("aqui")
    print(request)
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
   
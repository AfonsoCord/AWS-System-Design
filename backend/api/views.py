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

aws_access_key_id="ASIAYS2NSE42CC3PZ2QF"
aws_secret_access_key="2aoODLhdcb4fJvdXRSYav9DaioJTajy3pJvX2aAf"
aws_session_token="IQoJb3JpZ2luX2VjELb//////////wEaCXVzLXdlc3QtMiJIMEYCIQDg+z/qT8HYlKH7TVgVLMVxWLmXik8DrKqobxpC203yXQIhAIIweSdZGf+MB3B0+UecFmA5KQ8vGChyxG/WMvib/h2/KrQCCH8QABoMNTkwMTgzODAyNjc2IgzsvC36iHF1x3bLL+AqkQIaN7va2UAT/Oa9y9kT+h9KTUulADTL4+LQmt2IdHC2VxF+GpkGhblWrv0qWpNplzjax2fj91PzdcGeL2hWMm7vwoVMyrhQNmcj71Fw8OyhvTVCLQ7il6FLexcK6Qs9cYE9AhgxFZibQ5ZCB2dpFJxdNfeRzxKcEu9gtOmld765AbWsRmeOOGXES9a2lxxxRh+dxUJFRPMGtxOY3pR8HxblvKmC85dSxuNQypqNSKUamKQ/WJFstCyH0FFZKpAbFrvB6dC4YRG/fEKhxfowLHGccruBolOEgpeguC+XtKhvR7BmJle6lOTDQeZ6Us9gPnCRDSTzXcXhVnAl80PKu2lXifs09fYniuWXlmO6KiOf/44wjKGSuwY6nAE+mKoXZS9gASYZ+3uVwVfaiIMj1JHhtHRXMU0TJ/SUuZtqIRUA1PBwxcEGIDnTIk1LuMpXGqKU33RokMtozuUQLyIMWINDev7HGdVvD+iXSszdKTcQjeU4/PtVYXWV47O5OxZUrY+FShvBD4Z8NnzxIKNADNLVmEiixDeSp5RG2T37UZYZcxAoIQ7gramKFaHTZHmSwxbWZsh20ww="

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

    if user is not None:
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
        return Response({'message': 'Invalid email or password', 'valid': '0'}, status=401)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def loan_simulator(request):
    if request.method == 'POST':
        serializer = LoanSerializer(data=request.data)

        if serializer.is_valid():
            Quantia = serializer.validated_data['Quantia']
            Tempo = serializer.validated_data['Tempo']

            simulacao = {
                "Quantia": Quantia,
                "Tempo": Tempo,
            }

            return Response(simulacao, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
def home(request):
    return Response(home, status=status.HTTP_200_OK)





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
   
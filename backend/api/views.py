from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics,status,permissions
from .serializers import  Simulador,LoginSerializer, LoanSerializer
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
from django.shortcuts import redirect
from django.urls import reverse


bucket_name = 'bankingsystem'
collection_name = 'faces' # ficou guardado no regnonition não no s3

aws_access_key_id="ASIAYS2NSE42BZTTMACZ"
aws_secret_access_key="hWlXNWLMzymZLL3sROUEndUAFI9idUPDLsErUZtm"
aws_session_token="IQoJb3JpZ2luX2VjEIn//////////wEaCXVzLXdlc3QtMiJGMEQCIB3LgTgFD9XFFPL7/VINBHQNrTO0IAks3jyB3zlkFiGGAiBC0MnD3lskzfUqzR/OYyinhiSHV5aaEc+fN/stkoh2SCq0AghSEAAaDDU5MDE4MzgwMjY3NiIMKzQrCjmzYL5A9TN0KpECdcXyN26IlexK7DnWVsPwlkt89RbXhpcwFP/5KANHa4riBqExvs95/W/IX5MTlyMtSdxMKi3ZDvOpuvmwLCQaLOXsxw/YRsUp6YWUwVmKDZpWkzLJsZfM1k7YaZsiAr+IUkMStm6yFy/AdvrnDMeeXQJC5U6vSwkfBri28RvTxBWnLxHM5E4EJsTIoivNhxiZdCp+cFYPXSjCeT2Yyx+giBa5e9ovdTsdUeecZy+osMJakyfnSiapnpLJ73Z52FvqVn21F4X+QvdH9mQ6xz59MF8Rf+zVEPTJIKe5UjlY6/sNRh9XQurtOMORGmBuYs19GRc+NADs3qC8/pfoahNWO7uXW6J46zAT1nyQGZlMQqJ+MI2xiLsGOp4Bm8xpiFI/aSvACPbL9Sgnj55N4OFlTQMf/4eU0ezjqRqdkwQllyNPum896Sca3Yi1BHjD+1WqVJ/zOD0VFl7ZYGVJQTiO7d07qvrBpi8IjLX8aPDQh2obK5KnQ82q6FfM1L6unYeLHaBkh5Nle+1YJoVnZYotJm+dbSkiuYQ5UtSuEpKg7DNh9vOlPzYs1T1ZCDq1Z0bJruipDjS2xhk="

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

        print(1)

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
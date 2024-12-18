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

aws_access_key_id="ASIAYS2NSE42B2J6RZWO"
aws_secret_access_key="Al0YZUW3j+amHdsLTW/KdjH15wL+8oq/N4+6nFca"
aws_session_token="IQoJb3JpZ2luX2VjEJf//////////wEaCXVzLXdlc3QtMiJGMEQCIGqmTrdfkFcj20IJ8MfJ0awP+yjlwPc8DdEywJnsoGk0AiA062vSSv36y0qsnHl0DtYB0JjGIXTclwrYr1gwl1SXKCq0AghgEAAaDDU5MDE4MzgwMjY3NiIMDx+KqItfOZG+YECQKpECtf40ogWN/XioNiaeYYPUx3Uk1i0VP3/i0v8H4pdSpLhuq+sca6qLqmTNWzMgl+dgq16dIP1Zwdbooy6oAj91wOGiX/pyOzQb0oht27y7j/98Ljv8qpuC6NAdslRkp+o8UVpSCHAquS096fE4WmZopay+sgCw3y08SxmpqX054KPNMcmOKJA96mgFHM15OHN/jFxDp7IpvdrG33M61No9VM93C6DlaAETx9pYwqptNpzyQyC8Ln8dsElVg7UshLZuo6mUUtG5tyhdqPOaQ5Fi8gCqeeYqkI5RVtH+CmJpFh0geYeU7YJ5hcnAlFLDv8Foq71Ky0d2av9mx9wurzuPqD8O3rHkg+UZ6odYHKB5y2tjMMPFi7sGOp4Bc60VM0Pxj8c3lfvVjc3zFyCYE8c+2Ez4nzSUUB5yU5Ojw+fRO9bEItyNrEkYGbcXAyBmAwuk5O+mm2J5pXv/LvViccrBylrrnCe9gD7IprTREAOtl+sBEqCLvZfrDPNqimspqvOcIrayRucfJAur3BaUpHPavsfHMdSTTje4/42y7Ol/YmLikU7S4qxsfI1qvNuc5dPXB7tm8mGUhKc="

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
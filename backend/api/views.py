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

aws_access_key_id="ASIAYS2NSE42BYK4P5NV"
aws_secret_access_key="Z6zTBAxXXUxBecLLi2MPuagUQEof7OdvuaI4OQzX"
aws_session_token="IQoJb3JpZ2luX2VjEJX//////////wEaCXVzLXdlc3QtMiJHMEUCIQDbpTyTY2OprrpNvc8ybf3wIjE4oY7CnHD7Tz2yCzTTTQIgQoxZFzJQHFlPGlnbPJFpjKypZm27IRj/6gIeOdOPE10qtAIIXhAAGgw1OTAxODM4MDI2NzYiDAz/uWWfaxf4nZpeuyqRAnH4uxmgbdZB/KzYNXjinDC6ZVHZuABZBZM11x2pVWFzS8Z5gKv03I8ZBZLGl1udNuMRsVhwtfAnVyv3Cot3C/cawlwp9od59SAW7vxynEpHomW5jUWw9DFQb/7gGfbhCv3IBFu5wla0+NVD+d2Q/Q773ApT06EXoAQ6sTilqdB5NQR0EGDdEisneQOA7hrvLzs1eS34iTYDmJLFbDaPlItrlsOVWeJqZ8y8vhwhcq9MhTTILwNdK1q1TAFnFGtVRm+zhTmXECjNHt+80pAS4dXDi7OTO5uAloOwB9r1E3uKXCG0C4vsglln+0wjk7+hpbhAInifDn31Lw3M4XQnOmj5YxRrCjzg9rTng3Kn6MnYNDDvgYu7BjqdAd7xUHxV8J0s2xiNVvUz50dxpv1Ijj5rI8UaCdTT2pEHmgcnIVFGLQ6+DVjdoF9N2u5gdevoLMZOnDlBDHqtjYuXdqF9c6delRFguEzUZIbeoq86gKM8zbQXM+HXrO2VXZ5n2zEh9sVI0irOP4LG5M6EGEvylyECxYSjnx/kiTfyi72ylmoSw5ZrFbEQSS7EKROUlWMv+aFmXNCUvME="

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
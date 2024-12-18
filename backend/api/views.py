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

aws_access_key_id="ASIAYS2NSE42PUOMS5XN"
aws_secret_access_key="jV27+dtl4Hcn2AxA3bg0f1l8LDY6ahTnUv90vEyC"
aws_session_token="IQoJb3JpZ2luX2VjEJv//////////wEaCXVzLXdlc3QtMiJHMEUCIBHRfyCWE5vQnlvkL/jMI0jawn0fDmQnQSGN11z5XpwBAiEAs0RweMT8VCj3jpOOaZ8hoOACsyO4X2jRONicwmxlmLYqtAIIZBAAGgw1OTAxODM4MDI2NzYiDFOG74ctOpqUIfwkUyqRAoMU+ej4j1TPvWJhQb2n4yXlNvQBnZHytvP2kEJu6YWHyhYUDGpoJv9blx3SRmFNef0TatbqDzFJHU1Rww+z9G/xWaVbN+8boGnpY0/peLChMqmlq6UcDSZeaj7MQS21ksoQfJ8CWJdMR3CnT5U0bhnBPYAZqvVgXB705hncdB39G+TuBIZfny5reuJ0BWaHKpNM+PlFKZKjHZA3/8JhWKuab39eDTmC52EZeuiitxAzPqYTmRc9f9B5ILsq0UWOdPmSCTqQZbOo3u8YZZcEa7kM8dWpsNYpoBEcMyKc5+58NUn7koMrNy6H4Q4CxNB/OmxfpkFqqINUUHSeD4sNZhCwg8zebmNU1hc55oqCngAfZDDOqoy7BjqdAZTnYz6nd50khsakDZktEu59QWOgqjmKrue8adQwWMdy6Vg3r4AZH+MXQKHsaFtKPyqfbwpwTwoYgyFDfHYlmwiEKIZrnDUD49VPMgA+e6uvaBx8/0fO0F0h7MXK6iwicPmAc1k+r1JYymdYOAnHSQCmFtn+6edQIQSKpce1p6wv8h8SWjCyYSJP88svuk9LhkycChUP0i4LYkJR8k8="

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
def BankLogin(request):
    #user = emprestimo.objects.get(id_cara=id_cara)
    user = dynamodb.query(TableName="funcionario", KeyConditionExpression="faceid = :id", ExpressionAttributeValues={':id':{'S':id_cara}})

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
   
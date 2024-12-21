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

aws_access_key_id="ASIAYS2NSE42DSEVB7DP"
aws_secret_access_key="m39Ku+L3ta5p3CMWTqRF8Y2eQlRG7hSZVrZNYm5q"
aws_session_token="IQoJb3JpZ2luX2VjEN3//////////wEaCXVzLXdlc3QtMiJIMEYCIQC+kXiEnPT2TTmzx8Htpr5Y+NAxAUF8AQMt8se164MungIhAJDTFBK8u2tsYOwDocaZydyDRBBGEvIK2HA6rxPPVol4Kr0CCKb//////////wEQABoMNTkwMTgzODAyNjc2IgykCFr5b1ud0Evuez8qkQJ4fg9rqzigeGwNVdmEYydRMHsKOMovSoneMGud4GCivqv/qcbhAFcbjv89dSqWRU8k51N3OPTczwQZ+57HoIqECX65A4jakqAEneFQIMAx+pnfz687FSSsczMeWYIjLyLaP2sR3EEKwctFm6cIygnwjh5ryKRXMzfI/u+IjzvOxpQAwrq5GjF4a0SbiJ5eLb1G/q/VUYUEV9qstyHbPTty+LjOT8vRtiqSj8wZLh1/V3bT8S+NX0aePozk/R5GFyw8iv6tgmhpl25/Q4nIw51e9zqv8Hi3XhoGs6FHlwJRXo+c1IlR7tP9SUpX/sEVVurmL5S4usn+K8qXVLCrEiXB65vEVCINLvR13bzu62T5l0ww4+mauwY6nAGv5NFCf67fEIaR+yaAPCsPfsgGhFIpcz/9taKVlV9UZtQLy7mLCoA84fs3kchN9JNNYVxRnKOmq8iLpHzjLlLp2Zg7b5KizJMMyLFO7EpSbqsoxYsI5WymEd/8NCis4ebMZBKjWsxB56vpiWBVDH+xruL6zKIQqW04uXvbuODT90bT27ubBVsKKBD0YNMCJMhYkthZdqn0NypH+UU="


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
        request_data = request.data.copy()
        request_data['person'] = request.user.username

        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save(valor = request.data["valor"],
                            duracao= request.data["duracao"])
            
            return Response("Parabéns!",status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
@permission_classes([IsAuthenticated]) # acrescentei isto - matilde
def Home(request):
    print(request.headers.get('Authorization'))
    serializer = LoanSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(request.data)

        emprest = emprestimo(
        valor = serializer.validated_data['valor'],
        duracao = serializer.validated_data['duracao'],
        salario = serializer.validated_data.get('salario'),
        profissao = serializer.validated_data.get('profissao'),
        documentos = serializer.validated_data.get('documentos'),
        tiposempr = serializer.validated_data.get('tiposempr'),
        estado = serializer.validated_data.get('estado')
        )
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
   
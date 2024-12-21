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


aws_access_key_id="ASIAYS2NSE42DD4EFXFA"
aws_secret_access_key="YDGNXF4PcBiyMzAMokqm0SXlnnx/th3FClWQkxpi"
aws_session_token="IQoJb3JpZ2luX2VjENL//////////wEaCXVzLXdlc3QtMiJHMEUCIQCeHkHPEg4OkqNdn7p/KhZfsPqsrRnT5eFrLSxa+q2oXAIgBT30lsZxL9Kn31zH9W6U+cx1/dQAoPqv96Ht2NriTB0qvQIIm///////////ARAAGgw1OTAxODM4MDI2NzYiDIta+ft5FQ+XKYn6JCqRAl7v9bgCrh7Of5Uf2eWnDjROSWT6kuKmeQR3Qm7ka9Q9QayPSE5uo47P56PC6a0Th2YnAivxGQuiHU9CdkEAUaSswABhwOT66G6X78S2o80CDQqBxb7jY+Qb9ZMPcH4h8DsDqMC2q7DkM3dsFv9tJxMClfR01Geb+lDmzEK7vpBLJ07lR4XAVFn6DAOLWc56I90LMjbk21yTreDGfyfSzuRqWlJP5Oz6ZvdAMqW48S6T4+A7PrmFXvA8ilINq8DI26DGMvfF/YjJJqezmjCIYrDHaFIW03l8AL/QS/U2/B4A2NOJ8I0+Siwl0KiVhNMn/7hHUbJ9JcTpe3BtyYoxEfU3BNxmHxyfoD0m7Uu+0ctMdTCRw5i7BjqdAat+tifRZwRzF8J6ZrSJmwV49edYiak0T2UrrISpPcKcr1o/esFqhOMQbouqCHivWNBKBAD1ppJLcbisgqX5oRai0XBJt6Bb0CEPpUef3qN+MdB1Ac0ghyhVv/sIe0wL5tmWDVqSCtFSVunC5FmeJCaHWPn9UwkM7F7dJpulUFLd364emUGi8GrZt5CMHsw5/O+fkdDQV2dzUdpo/EI="
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
def Home(request):
    print(request)
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
   
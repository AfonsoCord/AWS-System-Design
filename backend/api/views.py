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

aws_access_key_id="ASIAYS2NSE42CLDNQAGW"
aws_secret_access_key="MtKPXdRQRLrK5lGYDOUtf084FAfF+/zOjwxMTJ8V"
aws_session_token="IQoJb3JpZ2luX2VjEBsaCXVzLXdlc3QtMiJHMEUCICJVGaOx+qVYrEn7JFWnQ8jvTZnWhdNzw9Si6spYVdblAiEAy0Kk4QBD28Vopeb+LGXU56mHcLfyVwm76miBB8IhlmMqvQII1P//////////ARAAGgw1OTAxODM4MDI2NzYiDIaXvc3cPQUJRW71zCqRAuPzFiq6/4AtkxJhmmim4bvJgK0VKMAK1oGWZzyCzbqW2FkCzjCuCnU1SSnDilrpt5zE+RaijUfRx5UiB0nu3UKAy3BwB+xrrVDNYB0EU/X4UMAWk1Y8Ntlstf195pYH2w2mtGkKVzilyJHM2ol1lf2NXs6u3mXHlbG/JIXar21PW5n79TOv5jpDJAscGhj/mXvntBnRs2uXBpFMKYeo7/zbFUIjk2Y5AtFoVNr6og6L584nLEbZmuDvA4+hCrqtndkuNtspBgkFoC8YIHjSVvPpokOsKEgzvYC3wEyxHmqH42WT8GusmtItsJkdXhWuS6//VNAsQ2hSpwqNFjmCHkoYRYtS/6M2SAIl7loh+tGpwTCervC6BjqdAeclqTuHXvwOSrZT8X9DpgBRmbzKxcnvtWdorQPeYJR95lj9K+Sfkvfrw4Iv72JOVThIcA1P+27KpOmvVzPexMgGSl/6baMoULBJzApsf3xhyJ8VYoQmk6vfKLRytuey8HqfAMTeZYzQurYg7yAlyqx50oZxFZBfbgickaZnKwe5INgJQ6bOntUMcPvkEYr+IOk4u8IC8plud76kWKk="

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

my_bucket = s3.Bucket(bucket_name)

class CreateUserView(generics.CreateAPIView):
    pass
    #Para nao criar um user que ja existe
    #queryset = User.objects.all()
    #O que vamos precisar para criar um novo utilizador
    #serializer_class = UserSerializer
    #Quem pode usar/ver isto vão ter de ser todos para poderem criar uma conta
    #permission_classes = [AllowAny]
    
class emprestimo(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = Simulador

    def get_queryset(self):
        pass
        user = self.request.user
        return emprestimo.objects.filter(person=user)

    def get(self,request):
        
        data = {
                "CollectionId": "bankingsystem",
                "Image": {}}
        
        client = boto3.client('rekognition',
                        region_name = 'us-east-1',
                    aws_access_key_id = aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token
                        )
        
        #A pesquisa ja funciona so falta ser na web que se mete a foto
        image_path = r"C:\Users\afons\OneDrive\Imagens\8643f1e8-8e42-41ab-a218-e413a9d56414.jpg"

        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()

        response = client.search_faces_by_image(
        CollectionId=collection_name,
        Image={'Bytes': image_bytes},
        MaxFaces=5,
        FaceMatchThreshold=90  
    )
        
        return HttpResponse(response["FaceMatches"][0]["Face"]["FaceId"])



    def post(self,request):
        data = {"teste":3}
        lambda_client = boto3.client('lambda',region_name='us-east-1')
        response = lambda_client.invoke(FunctionName='teste',InvocationType='RequestResponse',
                     Payload=json.dumps(data))
    
        return Response(json.loads(response["Payload"].read()),status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request): 
    serializer = LoginSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)
    
    data = {
            "CollectionId": "bankingsystem",
            "Image": {}}
    
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
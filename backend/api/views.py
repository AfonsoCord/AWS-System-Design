from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics,status,permissions
from .serializers import  Simulador,LoginSerializer
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

bucket_name = 'bankingsystem'
collection_name = 'faces' # ficou guardado no regnonition não no s3

aws_access_key_id="ASIAYS2NSE42E33L7SXN"
aws_secret_access_key="jdmPVjb2FP9lIEc/LHbZ8GwEWy8RQxwlgR4quRYn"
aws_session_token="IQoJb3JpZ2luX2VjEAcaCXVzLXdlc3QtMiJHMEUCIQCUkYH3HCyHcial/1JsqnUHyGBFDwhpCz5Vv0snCSurJQIgKYMqRqnkOTUahrjI8VfEq2k2z2s5LQbV+1EzjqjCCC0qvQIIv///////////ARAAGgw1OTAxODM4MDI2NzYiDKeSRblquFsNJEeVVyqRAjt/m1VPCdkBZWpj8FigJfSGYgwpOnX4b1ljr+JUdc1H47iwBe9+p1fPHw4QQLuXqakVPcJ+V7jYKOTtBPWDxNk/UE/+g11rVnJbVB6PTi4jMTtaaYJ1cL1Vxlfl91LqzD0Chdx1LjQxgMRTxinUyckzrWf5CDbwDciGsV4imzWnxQBPg1h2PmZsNUPZ4RzwOhgZiMlBipv2HFTxgqh5pBJzMahKrn36OYhXAPNfrbHUxYodej4D62/ir2Akvmga2lZ7HeYibCYWAzHJW9iHuhIdFcRdvYhaOuFVI7os/CQJeAHvRedEwbtoNefZYKkFxjp2eGoln8VLnH8vRZGLDg06mA4SKQbLyY4QYAsrZDuv4jCb4uu6BjqdAf51WXqFO1PgNkxCYf4Cu3vVo1dTNz5He/2iGxEOjxea8aumR83ujBcAWvEakFy6pdx7Zo0/VjrNuz1Uf/7BqED5LEzKr/ccaK6Kvf2P3jeV2Y8yVvXQlaP6Qx2UiC0aVpXmV3Yf4u0RNKef2atSk11i4fa7RuQvk3WZtDYAvsPU72qR1RUrDmhyy3+I9aOn5WClo3iR+6RPLP5lTTg="

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
        image_path = r"C:\Users\afons\OneDrive\Imagens\images (2).jpg"

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
    
@api_view(["GET"])
def simulacao(request):
    sim = emprestimo.objects.all()
    serializer = Simulador(sim,many=True)

    return Response(serializer.data)





@api_view(['POST'])
def api_login(request):    
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    nome = serializer.validated_data['email']
    id_cara = serializer.validated_data['password']
    
    user = emprestimo.objects.get(nome=nome, id_cara=id_cara)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'id': user.id,
            'valid': '1'
        })
    else:
        return Response({'message': 'Invalid email or password', 'valid': '0'}, status=401)
    
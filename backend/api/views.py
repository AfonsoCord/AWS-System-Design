from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics,status,permissions
from .serializers import UserSerializer, NoteSerializer,EmprestimoSerializer,LoginSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Note,emprestimo
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import boto3
from django.db import models
from rest_framework.response import Response
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse, JsonResponse

bucket_name = 'bankingsystem'
aws_access_key_id="ASIAYS2NSE42E2PSEQIE"
aws_secret_access_key="ClEz8ogw8m8hLAEI1uhhC8CVR4A5uTl1SuaGDaoy"
aws_session_token="IQoJb3JpZ2luX2VjEGIaCXVzLXdlc3QtMiJHMEUCIHElurZ+aR7NhUH1uLT2sr0Z8WXRQ+zRFs5oQwalX5mBAiEA6EMJgjwHJ9jYUQLUTk706UEsMIvKNKuE9O6EIdFUBNwqtAIIGxAAGgw1OTAxODM4MDI2NzYiDKKT46zpBMu5ht3dzSqRAnG7JjUibJIxMu1vcGx5LYWn3Xrghcp+IQrpE+hUpDn0TpU6INZDrKOb5UOJ01d9GqVkYoTXXa6M+tG1qtX//acLfYkdcOpjzOw9S99riGbBRXopCzVmiubGCWi8Qq6ydwSRxIlHzO8OCbAGKB/Jr8oZ+2f91NiiH45s/xH4nR+U5ah7mGiLSm8gOgCzPBBPlcZla7OWbAPTQ55TbQGtl0xo54JpQPticb2XVUo0CK/MmhcCmWm7bM0FlnFl+mTHwajR8LFHySk0ZDhzBVVmUnXeOIiE0zZPMHpChMc9eUaT3p6fSLZEPYK94mjFFzmFAmM3j/hZ+JiCnMSlveT2ix6pmnHAYmO3n0WbyxEA9p2g0jCb3Me6BjqdAfyxYxy3Wdl6tk18xDLT2FAxNGHYQFwewdFRncB3I31fOvedyREwvSmEtAKLTT1MVWsT+aa6O0DLyouD7vSrxoPuXW8tURxBVJgRjGzeaW/xRm9G4dDrtnsKPUWTBUyiPmCBo78S+RDMS9p/cfVFUOvhidnm5XhhrSc4B/56HHSD34vkKaYzZ7j78u8bt9GWOlBmD9TAqFnhjCo+8IA="
collection_name = 'faces' # ficou guardado no regnonition não no s3

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
    #Para nao criar um user que ja existe
    queryset = User.objects.all()
    #O que vamos precisar para criar um novo utilizador
    serializer_class = UserSerializer
    #Quem pode usar/ver isto vão ter de ser todos para poderem criar uma conta
    permission_classes = [AllowAny]

class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    PermissionError = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)
    
    def perform_create(self,serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)

class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    PermissionError = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)
    
class emprestimo(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmprestimoSerializer

    def get_queryset(self):
        pass
        user = self.request.user
        return emprestimo.objects.filter(person=user)

    def get(self,request):
        
        #A pesquisa ja funciona so falta ser na web que se mete a foto
        image_path = r"C:\Users\afons\OneDrive\Imagens\images (2).jpg"

        with open(image_path, encoding="utf8", errors='ignore') as image_file:
            image_bytes = image_file.read()

        parametros = {"CollectionId":collection_name,"Image":image_bytes,"MaxFaces":5,"FaceMatchThreshold":90}
        
        #"Image":{'Bytes': image_bytes},

        stepfunctions = boto3.client('stepfunctions', region_name='us-east-1')
        response = stepfunctions.start_execution(
        stateMachineArn='arn:aws:states:us-east-1:590183802676:stateMachine:MyStateMachine-664xyq4uy',
        input=parametros)

        return HttpResponse(response["FaceMatches"][0]["Face"]["FaceId"])



    def post(self,request):
        data = {"teste":3}
        lambda_client = boto3.client('lambda',region_name='us-east-1')
        response = lambda_client.invoke(FunctionName='teste',InvocationType='RequestResponse',
                     Payload=json.dumps(data))
    
        return Response(json.loads(response["Payload"].read()),status=status.HTTP_200_OK)
    

class FormSimulacao(generics.ListCreateAPIView):

    def get():
        pass



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
    
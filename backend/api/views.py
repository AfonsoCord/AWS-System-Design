from rest_framework import status
from .serializers import LoginSerializer, LoanSerializer, BankLoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import emprestimo
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import boto3
from rest_framework.response import Response
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import permission_classes


bucket_name = 'bankingsystem'
collection_name = 'faces' # ficou guardado no regnonition não no s3

aws_access_key_id="ASIAYS2NSE42NWERTTXW"
aws_secret_access_key="vKgaTUJn7gAW7vufQSFkC+rmxMdyr1zTrFs/xb2h"
aws_session_token="IQoJb3JpZ2luX2VjEPb//////////wEaCXVzLXdlc3QtMiJIMEYCIQCstTH++xE0RVReK8F/xInbO0d/+HTCVQrLOP3fJlazCwIhAIbVH9Gg956m8CTvqXWht3JEGJvYpnLrLrKTChKYt5k1Kr0CCL///////////wEQABoMNTkwMTgzODAyNjc2IgxBOdH3e5vqMhDDi/YqkQLxDwXBtJ94vtpVW2VGNL0Y94EL7GXh2PFvbPoZ5C6ZdMpgTIW9WaF2OxCVrZcepm6iJK9ruYhkdye5Z164PnNKNMaw90aP1kzBfMIx7uVZuH2/zEvSMiouyQr6vshk++JgaFqcur9Z/lkom+8vSPSI9L3rR/zcIpGnSJJvkLZc4FvJ7E2uZh584Pqd+xsTF0BK3l/h2unqEqyr1hln6FLQ9TE+fOhXYJbKlvG8zHkFce9VCinncx3zOzk+JvqI2N0sI3fKCJPtJMR1HgwQFKuJP33JEkUBAMwWVkXvg1ft4SY2GBDuiOar0kx3HlFfMhBLc8knmSbO0D7nGRDf/OACeJRf+yjf7X/AAa1l6Rm1wwYw/6mguwY6nAExo0IbKz/2JSUcb4kpiDnIBURFYWIYXKPevpSRaCRRCEkPtOsO2CXXpBUBKGJexeorcZWYeJjiP8z9SXDXBJzji+5tAXFfy4IzYlDnKcwgSi2/xfyfYLG+VSwxMgRLX93czzlUJOLsYNrulYMOLvuvoCvYxnM61JvZDXozzF227PL3WwF1HhkeqiMp/fckAWh4GswEtYY3xbgY57A="

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

    try:
        response = client.search_faces_by_image(
            CollectionId=collection_name,
            Image={'Bytes': request.FILES['photo'].read()},
            MaxFaces=5,
            FaceMatchThreshold=90)
        
        id_cara = response["FaceMatches"][0]["Face"]["FaceId"]

    except:
        return Response({"message": "O reconhecimento facial falhou."}, status=status.HTTP_400_BAD_REQUEST)
    
    user = dynamodb.query(TableName="utilizadores", KeyConditionExpression="faceid = :id", ExpressionAttributeValues={':id':{'S':id_cara}})

    if user['Items'] != []:

        # Criar tokens
        refresh = RefreshToken()
        refresh["user_id"] = int(user['Items'][0]['id']['N'])
        refresh["username"] = user['Items'][0]['username']['S']

        access = refresh.access_token
        access["user_id"] = int(user['Items'][0]['id']['N'])
        access["username"] = user['Items'][0]['username']['S']


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

        if request_data:
            return Response("Parabéns!",status=status.HTTP_200_OK)
        else:
            return Response("erro", status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Home(request):
    serializer = LoanSerializer(data=request.data)

    if serializer.is_valid():

        emprest = emprestimo(
            user = serializer.validated_data['user'],
            valor = serializer.validated_data['valor'],
            duracao = serializer.validated_data['duracao'],
            salario = serializer.validated_data.get('salario'),
            profissao = serializer.validated_data.get('profissao'),
            documentos = serializer.validated_data.get('documentos'),
            tiposempr = serializer.validated_data.get('tiposempr'),
            estado = serializer.validated_data.get('estado'))
        
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
        refresh["user_id"] = user['Items'][0]['username']['S'] # ainda tem que se mudar isto

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

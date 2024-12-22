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

aws_access_key_id="ASIAYS2NSE42ANP7NXVX"
aws_secret_access_key="C8p/+PI6SkN6UJ3ol2sSyo8VnDbxqmoOj3SbVAUV"
aws_session_token="IQoJb3JpZ2luX2VjEPv//////////wEaCXVzLXdlc3QtMiJIMEYCIQCXvUdVT097IIOc+C7nleHbOEPntuiRwANwgIUh2O8QmAIhAN5t9Sy1ALGP9aQwUNHR8cH3jNhxjeyxtB67BY0YQNwsKr0CCMT//////////wEQABoMNTkwMTgzODAyNjc2IgxOvj3f1h3CoRRILHcqkQJgeoSPPP7VN7hAkvJjBI+8NVyta0hjLeSmzHnQzP1e/xUa24txQxtI3limTd2Slk2vAOaRZFmxk5ULH/19yWpVvBfkOhRsrQXG00tDD10nksCyfaiLay9azCfCNTJzqroyfVsjzBczM76SuI8YoIPH+tby0aqVJL2S2wwq0HuNLWHESvvpnyUQFn5fv5HOLJyLgZjhOAMtMquzqxbX61OF0Tad91bg/OBf9egoQbTCQ/4u8LuA1ug2t4prC4tCkDcsdWXih49Z20xSP2+uN7s2cMpHV3HjQ8Jazq5pPXlVTGigL1pSE+Jp/YGI0o/5lSyEqYTBWR2QO5e6iItdmYGxqwI6GxB38scuwsj0yAKbKIkwr7ehuwY6nAFr6S+AFWLM1rhE0097katk9OV94W/7CfRW3XRbhN3y+bw7C3SV+hJRdR+qDGmB262ftlhxI5vmt8vp4LnD0UBsazmGcg4k+uBZB/GSE2hsjqqumy/HZRv3mLOUPzXsvxnh86Fsv5n4G+BCJ3V++Xk+XrDgad3s6l67pWTiIYx05ooRKUzbd0SyxX/kt/Gl+jkPrw5qldvse6u7VgM="

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
        serializer = LoanSerializer(data=request.data)

        if serializer.is_valid():
            return Response("Parabéns!", status=status.HTTP_200_OK)
        else:
            return Response("Erro na simulação.", status=status.HTTP_400_BAD_REQUEST)
        


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

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

aws_access_key_id="ASIAYS2NSE42MR22NVIL"
aws_secret_access_key="HGFj5wUrsgJEwuER6R+6kxHH/NtJQH7rB0618e6z"
aws_session_token="IQoJb3JpZ2luX2VjECgaCXVzLXdlc3QtMiJGMEQCIEvQ6WbEYefxt6G1sV7sdi3jsGz/oVxvJFVwHqEK/GYmAiBTLPSBMmQd22yz4rTTscEnpolyN5BbToOO7Lkg14yh4Sq9Agjx//////////8BEAAaDDU5MDE4MzgwMjY3NiIMNLqD12pjqaWSFh2OKpECtiHVbfMDFJN4L3GS0eIljPHsQtqONI9ZQ1BUVsVlgDpBIG2ne5rxY5XnnuevakkYy6ZxdLz4WuFvlEtwd0arTPeOWrtNLgmj3g1mTm5JEbU+rv0wIxZl9/jSWK0BJjzLf7yhgzRyrIffSMsAhha7oh/Z+B1LFYvMcoDdPRSWFHYf3ISW0f7vt7Q08hQrTE18wdLF0mqU3AzlH76dBgf4LV5Cm+evsMXbHhoPpS+tvfagPYnXOFC45+NHhJZcRUBad3PBDG8sP4dBL5VSA/jS1gLtNPoSTQPgLnl6teQSxcj3pExgMu1dK7PO2WTOzCPDlqmzhHW9zN4TjM7NbnYJTXx9m7rYLjgIArSvZCEw6K7bMNyrq7sGOp4BX+cH6L+xeB3rmywmd82saaddBoB8xhJIf46HZBwd3HIj20K4gk7o8uHFiFqdCy+6iFP5fnpCkIsBu0y+aKqeFfoSv17dL0UOyQ80t+eYqPFZRKNxof1a9MMF4huhhTv1EqG3ASYZ8xEDJofhIfHb19zZMKns0dVRNVIgbjW5pxVe/aTbHqXnkgGAH3RdmGM8gGlg10oWIV0m/MiSwjI="

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
    

# estado do empréstimo
@api_view(['GET'])
@permission_classes([AllowAny])
def loan_status(request):
     
    username = request.GET.get('username')

    if not username:
            return Response({"message": "O campo 'username' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    emprestimos = emprestimo.objects.filter(user=username)

    if not emprestimos.exists():
        return Response({"message": "Não foram encontrados empréstimos para este utilizador."}, status=status.HTTP_404_NOT_FOUND)

    emprestimo_data = [
        {
            "valor": emprest.valor,
            "duracao": emprest.duracao,
            "salario": emprest.salario,
            "profissao" : emprest.profissao,
            #"documentos": emprest.documentos,
            "tiposempr": emprest.tiposempr,  
            "tempo": emprest.tempo, 
            "estado": emprest.estado,
        }
        for emprest in emprestimos
    ]

    return Response({
        "message": f"Você possui {len(emprestimo_data)} empréstimo(s) em processamento.","emprestimos": emprestimo_data}, status=status.HTTP_200_OK)
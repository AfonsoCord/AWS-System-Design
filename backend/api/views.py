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
from rest_framework.permissions import IsAdminUser
import pymysql

bucket_name = 'bankingsystem'
collection_name = 'faces' # ficou guardado no regnonition não no s3

user_name = 'LabRole'
password = 'projetoes2024'
rds_proxy_host = 'database.c3oqw4668mx3.us-east-1.rds.amazonaws.com'
db_name = 'emprestimos'

state_machine_arn = 'arn:aws:states:us-east-1:590183802676:stateMachine:MyStateMachine-nslqfmw27'

aws_access_key_id="ASIAYS2NSE42N5NWP7QM"
aws_secret_access_key="RWkfiGg42WjTR7uFEVsqrGlLJO896iJ1BnFsuAPj"
aws_session_token="IQoJb3JpZ2luX2VjEGEaCXVzLXdlc3QtMiJGMEQCIGyqy4VXdhaHoDNgZ7JgmwvNrmh6fIEM2VHKUdrdWrdUAiB3tOvnpSvUXaWm2p58T1LrR49td+0LmRq5hCvpyfMNyiq0Agg6EAAaDDU5MDE4MzgwMjY3NiIMzL1pma1wP4AtS+3BKpECxWgIlY74IEHoiWAMuxMHFyQEAYicNN31QvVCgm2F31gE8Xd9Z67lHuKy4/uRP2Id0sVdhIwA7XAc1lc1k02KPX6/ckcv7rIKHNJEGkIk2oKsbsmN3dTakWXBcDqKh8debSOt6/t+nmG1XPyN7meELP7f9yVknVI5+xJfxv/UfFlfElcHW2hl/ulyADW0zFBqsWwRt+Z3gSomJ55YpI6OJTkRgPM5HQVzQk+4F0MeMIWSxvQZqzHFrFxfeX7pUuC7HakndNNgIevwLZkawA8r2k1iF8i2bA1OuddVAFVvrlei+beNgMYT7mTxcGamDpvw2jbWfad78mmNVQ6LhZ84Nwz7RZkBh2hPD4lt1o2CKxX4MIz/t7sGOp4Becm/9FJ8Valf4E9L65ahYDljLw8sCJdgFRsEPxtaYcpXE1wCsJ7Kvwg10dnIyWLyhRmhBlbs6Q+I37ujAy2zSUW7e0MaVzOOIht6zbIn3FyOj0uMmQ0fMhsxaGesmd8nWBov3TCEmOdtvg2lyqAeeJQYSQqGIrJYAws1TBrxe1PDfDmlDcudR2+EZofTOpPa6Gwv7e/hDCKFDDglmKg="


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

stepfunction = boto3.client('stepfunctions',
                    region_name = 'us-east-1',
                aws_access_key_id = aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token)

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
        refresh["role"] = "cliente"

        access = refresh.access_token
        access["user_id"] = int(user['Items'][0]['id']['N'])
        access["username"] = user['Items'][0]['username']['S']
        access["role"] = "cliente"


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
    conn = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=30)


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
        user = serializer.validated_data['user']
        valor = serializer.validated_data['valor']
        duracao = serializer.validated_data['duracao']
        salario = serializer.validated_data.get('salario')
        with conn:
            with conn.cursor() as cursor:
                
                sql = "SELECT MAX(id) AS ultimo_id FROM `api_emprestimo`"   
                cursor.execute(sql)
                result = cursor.fetchone()[0]

            input = f'{{"id": "{result}", "user": "{user}","valor": "{int(valor)}","duracao": "{int(duracao)}","salario": "{int(salario)}"}}'
            
        stepfunction.start_execution(stateMachineArn = state_machine_arn,input = input)

        return Response(status=status.HTTP_200_OK)
    
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def BankLogin(request):
    serializer = BankLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = request.data['username']
    password = request.data['password']

    user = dynamodb.query(
        TableName="funcionarios",
        KeyConditionExpression="username = :username",
        FilterExpression='password = :password',
        ExpressionAttributeValues={':username':{'S': username}, ':password': {'S': password}}
    )
    
    # Criar tokens
    if user['Items'] != []:

        refresh = RefreshToken()
        refresh["user_id"] = int(user['Items'][0]['id']['N'])
        refresh["username"] = user['Items'][0]['username']['S']
        refresh["role"] = "staff"

        access = refresh.access_token
        access["user_id"] = int(user['Items'][0]['id']['N'])
        access["username"] = user['Items'][0]['username']['S']
        access["role"] = "staff"

        return Response({
            'message': 'Login successful',
            'access_token': str(access),
            'refresh_token': str(refresh),
            'username': user['Items'][0]['username']['S'],
            'valid': '1'
        })
    else:
        return Response({'message': 'Invalid username or password', 'valid': '0'}, status=401)

    

# estado do empréstimo
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loan_status(request):
     
    username = request.GET.get('username')

    if not username:
            return Response({"message": "O campo 'username' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    emprestimos = emprestimo.objects.filter(user=username)
    print(emprestimos)

    if not emprestimos.exists():
        return Response({"message": "Não foram encontrados empréstimos para este utilizador."}, status=status.HTTP_404_NOT_FOUND)

    emprestimo_data = [
        {
            "valor": emprest.valor,
            "duracao": emprest.duracao,
            "salario": emprest.salario,
            "profissao" : emprest.profissao,
            "tiposempr": emprest.tiposempr,  
            "tempo": emprest.tempo, 
            "estado": emprest.estado,
        }
        for emprest in emprestimos
    ]

    return Response({
        "message": f"Você possui {len(emprestimo_data)} empréstimo(s) em processamento.","emprestimos": emprestimo_data}, status=status.HTTP_200_OK)


# acesso ao estado de todos os empréstimos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loan_status_funcionarios(request):
    emprestimos = emprestimo.objects.all()

    if not emprestimos:
        return Response({"message": "Não foram encontrados empréstimos de clientes."}, status=status.HTTP_404_NOT_FOUND)

    emprestimo_data = [
        {
            "cliente": emprest.user,  
            "valor": emprest.valor,
            "duracao": emprest.duracao,
            "salario": emprest.salario,
            "profissao": emprest.profissao,
            "tiposempr": emprest.tiposempr,  
            "estado": emprest.estado,
        }
        for emprest in emprestimos
    ]

    return Response({
        "message": f"Existe(m) {len(emprestimo_data)} empréstimo(s) registado(s) no sistema.", "emprestimos": emprestimo_data},
        status=status.HTTP_200_OK)


# atualizar o estado e a decisão do emprestimo dos clientes
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def status_decision(request, id):
    try:
        emprestimo = emprestimo.objects.filter(id=id)

        if emprestimo.exists():
           
            estado = request.data.get('estado')
            decisao = request.data.get('decisao')

            # atualiza o estado e a decisao diretamente na bd
            emprestimo.update(estado=estado, decisao=decisao)

            return Response({"message": "Empréstimo atualizado com sucesso."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Empréstimo não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
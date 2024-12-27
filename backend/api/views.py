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
import pymysql

bucket_name = 'bankingsystem'
collection_name = 'faces'

user_name = 'LabRole'
password = 'projetoes2024'
rds_proxy_host = 'database.c3oqw4668mx3.us-east-1.rds.amazonaws.com'
db_name = 'emprestimos'

state_machine_arn = 'arn:aws:states:us-east-1:590183802676:stateMachine:MyStateMachine-nslqfmw27'

aws_access_key_id="ASIAYS2NSE42BTF4PNC4"
aws_secret_access_key="11g5kwlXkZjmKd4RJKne4SNXclGx96VR/d6ZXaHf"
aws_session_token="IQoJb3JpZ2luX2VjEHQaCXVzLXdlc3QtMiJHMEUCIQCUP7p/naKA3Kd405CYwNMeIpmKSMjlWiZHPzUX32ORgwIgUNmdL8xJZjPidLglrcaMIRtUbbh+Ijqm3RQCU6QgFV8qtAIITBAAGgw1OTAxODM4MDI2NzYiDMPLH/NmYeK1pdGMWSqRArdNKApgp801xyY2JaaV0K0afvI3kFBUUOU/N5N3e7sW5O4sIkfBBBC27Sic+5A4r9FdC/iftBGSP9KiehAb0ffW8sEBmRMtNilW43lH7juG07r2e4FB/hVqMrJa75xKR+LTRRZ1lpSnbdieDEQOlbZwvHwOC57XtJu/zjMK1Gm4LhI9zdJ+NoynVjHVkmLS2SxJzKOR31kTwK0zULpHvfCrfyLG+V8LBxfXmOlobYcX2MQCDNKeQTPDNdz6ig9rbXDSRg913D+O4Z4bGYdLaY4d1CcHKb4cxdjsgUKReeRT2dXhe6w8UodAUml5nM6g/0tAt1H/nfLC51RLEANulpztR/Sl/YwHigCXV3svY8TDDjDA+7u7BjqdAVZKMAm92kcxUUMYx22m/LUO35EayZCmWBixzY09BVZvsu7T6ju/tDDzVOJQQISwWyAcKwpOn/mpyxF2JcTS+rBMtaMgsqukUHtHf+uiCc4BvJYH8BrRkQUVxR+tA/xv7nRi0oktdqSz76kfKcHTBP8Q08mJM/rkbfMKvtNsLhYXdHjRxDpq8/TSX9SwXSj0L41bCzWdgGcxQXeEiSM="


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
        # procurar id da cara
        response = client.search_faces_by_image(
            CollectionId=collection_name,
            Image={'Bytes': request.FILES['photo'].read()},
            MaxFaces=5,
            FaceMatchThreshold=90)
        
        id_cara = response["FaceMatches"][0]["Face"]["FaceId"]

    except:
        return Response({"message": "O reconhecimento facial falhou."}, status=status.HTTP_400_BAD_REQUEST)
    
    # procurar utilizador na base de dados
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
            'message': 'Login realizado com sucesso.',
            'access_token': str(access),
            'refresh_token': str(refresh),
            'username': user['Items'][0]['username']['S'],
            'valid': '1'
        })
    else:
        return Response({'message': 'Utilizador não reconhecido.', 'valid': '0'}, status=401)
    


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

    # conexão à base de dados RDS
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
                
                # obter o id do empréstimo que foi adicionado
                sql = "SELECT MAX(id) AS ultimo_id FROM `api_emprestimo`"   
                cursor.execute(sql)
                result = cursor.fetchone()[0]

            input = f'{{"id": "{result}", "user": "{user}", "valor": "{int(valor)}", "duracao": "{int(duracao)}", "salario": "{int(salario)}"}}'
            
        # iniciar o workflow
        stepfunction.start_execution(stateMachineArn = state_machine_arn, input = input)

        return Response(status=status.HTTP_200_OK)
    
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# estado dos empréstimos do cliente
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loan_status(request):
     
    username = request.GET.get('username')

    if not username:
        return Response({"message": "O campo 'username' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    emprestimos = emprestimo.objects.filter(user=username)
    
    tipos_empr = {"CHAB":"Crédito Habitacional",
                  "CAUT":"Crédito Automotivo",
                  "CEST":"Crédito Estudantil",
                  "CPES":"Crédito Pessoal"}

    emprestimo_data = [
        {
            "valor": emprest.valor,
            "duracao": emprest.duracao,
            "salario": emprest.salario,
            "profissao" : emprest.profissao,
            "tiposempr": tipos_empr[emprest.tiposempr],  
            "tempo": emprest.tempo, 
            "estado": emprest.estado,
            "decisao": emprest.decisao
        }
        for emprest in emprestimos
    ]

    return Response({
        "message": f"Você possui {len(emprestimo_data)} pedido(s) de empréstimo(s).","emprestimos": emprestimo_data}, status=status.HTTP_200_OK)



##### Views para o frontend dos funcionários do banco #####

@api_view(['POST'])
@permission_classes([AllowAny])
def BankLogin(request):
    serializer = BankLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = request.data['username']
    password = request.data['password']

    # procurar utilizador na base de dados
    user = dynamodb.query(
        TableName="funcionarios",
        KeyConditionExpression="username = :username",
        FilterExpression='password = :password',
        ExpressionAttributeValues={':username':{'S': username}, ':password': {'S': password}}
    )
    
    if user['Items'] != []:

        # Criar tokens
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



# acesso ao estado de todos os empréstimos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loan_status_funcionarios(request):

    emprestimos = emprestimo.objects.all()
    
    tipos_empr = {"CHAB":"Crédito Habitacional",
                  "CAUT":"Crédito Automotivo",
                  "CEST":"Crédito Estudantil",
                  "CPES":"Crédito Pessoal"}

    emprestimo_data = [
        {
            "id": emprest.id,
            "cliente": emprest.user,  
            "valor": emprest.valor,
            "duracao": emprest.duracao,
            "salario": emprest.salario,
            "profissao": emprest.profissao,
            "tiposempr": tipos_empr[emprest.tiposempr],  
            "estado": emprest.estado,
            "creditscore": emprest.creditscore,
            "decisao": emprest.decisao
        }
        for emprest in emprestimos
    ]

    return Response({
        "message": f"Existe(m) {len(emprestimo_data)} empréstimo(s) registado(s) no sistema.", "emprestimos": emprestimo_data},
        status=status.HTTP_200_OK)



# atualizar o estado e a decisão do emprestimo dos clientes
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decision(request):

    try:
        emp = emprestimo.objects.get(id=request.data.get('id'))

        if emp:

            # atualiza o estado e a decisão do empréstimo na base de dados
            emp.estado = request.data.get('estado')
            emp.decisao = request.data.get('decisao')
            emp.save()

            return Response({"message": "Empréstimo atualizado com sucesso."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Empréstimo não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
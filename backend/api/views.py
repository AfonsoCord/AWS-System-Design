from rest_framework import status
from .serializers import LoginSerializer, LoanSerializer, BankLoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import emprestimo, horario
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

aws_access_key_id="ASIAYS2NSE42IITZHICQ"
aws_secret_access_key="IaUzGpm5gd3aJk/t6MhB7PC9Rhr9ZZLrBxR43cEE"
aws_session_token="IQoJb3JpZ2luX2VjEIX//////////wEaCXVzLXdlc3QtMiJIMEYCIQCx+iLLIXQKcYAl+GPdci3gfxpVN4FWYcxZuZRmgblQBgIhAJvtBBMxYHXImxWtPT/bVHhELc8smsjX4h2v7g/anXAAKrQCCF4QABoMNTkwMTgzODAyNjc2IgyjVUj6MZ1d+2CyO38qkQImw+GCst9rzlT0hV4X7UeZIXuQbmBqLuggn4StEEgAo7H0MplV2garKLeNvOUB4RDVehO3LnMf9cwTbwQN18KiD1O86LYqJP4VgC8ZQvwqGYrdtImwHy+tH/sgkQedlz7Oz2XFeRuSMVV+xxGJqGikuCecxfigLA2AFUg80GvXRjfNlfD44DUPHyXSct8LN651EHGrY5sXJUA+R9bxGg9VzYSwKcJMIaM1ILiQIieq/ndcyVnmTzPeDNU2TN7xyO5OOFnCeKt2yUvH1ehAHioz4GHf/SC1XuXr23abZS0/7jCCl1WDkI7EUyPdc3tNjBW+Bwtt4QxbNDgNPibK4ihkhqwNnOw4z42IZYmKE0RVEVsw7t6/uwY6nAH+QkaoWMjk+904wYtqqQRLOyAzU/H7wD1HDf2QBTH7ILig+I6Nj0HRsjl/t1iySY7G/YGHEvWv9hw7juznE+miPY0MnhDWBcje4jH+e7+9Wa964aQTuQi2wEEX/yr599w7U/8ratzIsIIgNSEInHEbW/oJwn3wx1NmEWzWtxzZsWVrzeiJH6+3UA2+M2+GnSI40ACAry7N90tJ7Pk="

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
            "decisao": emprest.decisao,
            "horarios": list(horario.objects.filter(id_emprestimo=emprest.id).values_list('horario', flat=True)) #lista dos horários
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

    id = request.data.get('id')

    try:
        emp = emprestimo.objects.get(id=id)

        if emp:

            # atualiza o estado e a decisão do empréstimo na base de dados
            emp.estado = request.data.get('estado')
            emp.decisao = request.data.get('decisao')
            emp.save()

            # guardar os horários da entrevista na base de dados
            horarios = request.data.get('horarios').split(",")

            if horarios != [""]:

                for hora in horarios:
                    h = horario(
                        horario = hora,
                        id_emprestimo = id
                    )
                    
                    h.save()


            return Response({"message": "Empréstimo atualizado com sucesso."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Empréstimo não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


# atualiza o horário selecionado pelo cliente
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def escolher_horario(request):
    try:
        
        emp = emprestimo.objects.get(id=request.data.get('id'))

        if emp:
            
            if emp.decisao != "requer entrevista":
                return Response({"message": "Este empréstimo não requer entrevista."}, status=status.HTTP_400_BAD_REQUEST)

            horario_escolhido = request.data.get('horarios')
            if not horario_escolhido:
                return Response({"message": "Por favor, selecione um horário válido."}, status=status.HTTP_400_BAD_REQUEST)

            # funcionario
            horario_selecionado = horario.objects.filter(
                horario=horario_escolhido, 
                id_emprestimo=emp.id).first()

            if not horario_selecionado:
                return Response({"message": f"O horário '{horario_escolhido}' não está disponível, aguarde."}, status=status.HTTP_404_NOT_FOUND)

            
            horario_selecionado.cliente_selecionou = True
            horario_selecionado.save()

            # Atualiza o estado e o horário no registro do cliente
            emp.horario = horario_escolhido
            emp.estado = "agendado"
            emp.save()

            return Response({"message": "Horário selecionado com sucesso."}, status=status.HTTP_200_OK)

    except emprestimo.DoesNotExist:
        return Response(
            {"message": "Empréstimo não encontrado."}, status=status.HTTP_404_NOT_FOUND)
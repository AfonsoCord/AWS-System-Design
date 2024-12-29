import json
import pymysql

user_name = 'LabRole'
password = 'projetoes2024'
rds_proxy_host = 'database.c3oqw4668mx3.us-east-1.rds.amazonaws.com'
db_name = 'emprestimos'

def lambda_handler(event, context):

    # conectar à base de dados RDS
    conn = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=30)

    # calcular credit score
    credit_score = int((int(event["valor"]) * int(event["salario"])) / int(event["duracao"]))


    with conn:
        with conn.cursor() as cursor:
            
            # inserir credit score na base de dados
            sql = "UPDATE `api_emprestimo` SET creditscore = %s WHERE id = %s"
            cursor.execute(sql, (credit_score, event["id"])) 
            conn.commit()

    return {
        'statusCode': 200,
        "id": event["id"],
        "user": event["user"],
        "credit score": credit_score
    }
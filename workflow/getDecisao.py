import json
import pymysql

user_name = 'LabRole'
password = 'projetoes2024'
rds_proxy_host = 'database.c3oqw4668mx3.us-east-1.rds.amazonaws.com'
db_name = 'emprestimos'

def lambda_handler(event, context):

    # conectar à base de dados RDS
    conn = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=30)

    with conn:
        with conn.cursor() as cursor:
            
            # obter decisão do empréstimo
            sql = "SELECT decisao FROM api_emprestimo WHERE id = %s"
        
            cursor.execute(sql, (event['id']))  
            result = cursor.fetchone()[0]

    return {
        'statusCode': 200,
        "id": event["id"],
        "user": event["user"],
        "decisao": result
    }
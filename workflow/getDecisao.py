import json
import pymysql
import os

user_name = os.environ.get('DB_USER', 'your_db_user')
password = os.environ.get('DB_PASSWORD', 'your_db_password')
rds_proxy_host = os.environ.get('DB_HOST', 'your_db_host')
db_name = os.environ.get('DB_NAME', 'your_db_name')

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
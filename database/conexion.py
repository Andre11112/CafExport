import psycopg2
import configparser
import os

def get_connection():
    try:
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_path)
        db_params = config['postgresql']
        conn = psycopg2.connect(
            dbname=db_params['database'],
            user=db_params['user'],
            password=db_params['password'],
            host=db_params['host'],
            port=db_params['port']
        )
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        import traceback
        print(f"Error de conexión: {str(e)}")
        traceback.print_exc()
        return None
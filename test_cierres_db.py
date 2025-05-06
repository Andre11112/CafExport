import psycopg2
import configparser

# Leer la configuración de config.ini
config = configparser.ConfigParser()
config.read('config.ini')
db_params = config['postgresql']

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(
        host=db_params['host'],
        database=db_params['database'],
        user=db_params['user'],
        password=db_params['password'],
        port=db_params.get('port', 5432)
    )
    print("Conexión exitosa a la base de datos.")

    cur = conn.cursor()
    cur.execute("SELECT * FROM cierres_contables;")
    rows = cur.fetchall()

    if not rows:
        print("La tabla cierres_contables está vacía.")
    else:
        print("Registros encontrados en cierres_contables:")
        for row in rows:
            print(row)

    cur.close()
    conn.close()
except Exception as e:
    print(f"Error al conectar o consultar la base de datos: {e}")

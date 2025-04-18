import psycopg2
from psycopg2.extras import RealDictCursor
from configparser import ConfigParser

class DatabaseConnection:
    def __init__(self):
        self.conn = None
        self.config = self._read_config()
        
    def _read_config(self):
        config = ConfigParser()
        config.read('config.ini')
        return config['postgresql']
        
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                cursor_factory=RealDictCursor
            )
            return self.conn
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error al conectar a la base de datos: {error}")
            raise
            
    def close(self):
        if self.conn is not None:
            self.conn.close() 
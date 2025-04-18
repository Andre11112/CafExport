import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import DatabaseConnection
import bcrypt

def create_admin_user():
    # Datos del administrador por defecto
    admin_data = {
        'nombre': 'Admin',
        'apellido': 'Sistema',
        'email': 'admin@cafexport.com',
        'password': 'admin',  # En producción, usar una contraseña más segura
        'tipo_usuario': 'administrador'
    }
    
    try:
        with DatabaseConnection().connect() as conn:
            with conn.cursor() as cur:
                # Verificar si ya existe el usuario admin
                cur.execute("""
                    SELECT id FROM usuarios 
                    WHERE email = %s
                """, (admin_data['email'],))
                
                if not cur.fetchone():
                    # Generar hash de la contraseña
                    password_hash = bcrypt.hashpw(
                        admin_data['password'].encode('utf-8'), 
                        bcrypt.gensalt()
                    ).decode('utf-8')
                    
                    print(f"Hash generado: {password_hash}")
                    
                    # Crear usuario administrador
                    cur.execute("""
                        INSERT INTO usuarios (id, nombre, apellido, email, 
                                           password_hash, tipo_usuario)
                        VALUES (1, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        admin_data['nombre'],
                        admin_data['apellido'],
                        admin_data['email'],
                        password_hash,
                        admin_data['tipo_usuario']
                    ))
                    
                    conn.commit()
                    print("Usuario administrador creado exitosamente")
                else:
                    print("El usuario administrador ya existe")
                    
    except Exception as e:
        print(f"Error al crear usuario administrador: {str(e)}")

if __name__ == '__main__':
    create_admin_user() 
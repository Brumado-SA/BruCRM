from flask import redirect, url_for, session, g
import psycopg2

# Configura los detalles de tu base de datos PostgreSQL
DB_HOST = "192.168.0.111"
DB_PORT = "5433"
DB_NAME = "bruroute"
DB_USER = "postgres"
DB_PASSWORD = "Bru.159753"

def conectar():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def cargar_usuario_actual():
    g.user = None
    if 'user_id' in session:
        g.user = obtener_usuario_por_id(session['user_id'])

def obtener_usuario_por_id(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, documento, rol_user, cod_vend FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    if usuario:
        return {
            'id': usuario[0],
            'nombre': usuario[1],
            'documento': usuario[2],
            'rol_user': usuario[3],
            'cod_vend': usuario[4]
        }
    return None

def verificar_acceso(roles_permitidos=None):
    if roles_permitidos is None:
        roles_permitidos = ['admin']
    
    if not g.user or g.user['rol_user'] not in roles_permitidos:
        return redirect(url_for('no_autorizado'))
    return None
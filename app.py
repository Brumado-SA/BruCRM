from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g
import pyodbc

from tickets import tickets_bp
from helpers.verificador_acceso import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Clave secreta para manejar sesiones
app.register_blueprint(tickets_bp, url_prefix='/tickets')

@app.before_request
def load_user():
    cargar_usuario_actual()

def obtein_user_by_id(user_id):
    obtener_usuario_por_id(user_id)

@app.route('/no_autorizado')
def no_autorizado():
    return "No tienes permiso para acceder a esta página.", 403

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    acceso = verificar_acceso(['admin'])
    if acceso:
        return acceso
    
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios ORDER BY 1")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios', methods=['POST'])
def agregar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        documento = request.form['documento']
        password = request.form['password']
        conexion = conectar()
        cursor = conexion.cursor()
        # Obtener el último ID registrado
        cursor.execute("SELECT MAX(id) FROM usuarios")
        ultimo_id = cursor.fetchone()[0]
        # Incrementar el ID
        nuevo_id = (ultimo_id + 1) if ultimo_id is not None else 1
        # Insertar el nuevo registro con el ID incrementado
        cursor.execute("INSERT INTO usuarios (id, nombre, documento, password, rol_user) VALUES (%s, %s, %s, %s,'user')",
                       (nuevo_id, nombre, documento, password))       
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('listar_usuarios'))

@app.route('/usuarios/editar', methods=['POST'])
def modificar_usuario():
    acceso = verificar_acceso(['admin'])
    if acceso:
        return acceso
    
    if request.method == 'POST':
        id = request.form['id']
        nombre = request.form['nombre']
        documento = request.form['documento']
        password = request.form['password']
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE usuarios SET nombre = %s, documento = %s, password = %s WHERE id = %s",
                       (nombre, documento, password, id))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('listar_usuarios'))
    else:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()
        return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuarios/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    acceso = verificar_acceso(['admin'])
    if acceso:
        return acceso 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for('listar_usuarios'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conexion = None
        cursor = None
        try:
            conexion = conectar()
            cursor = conexion.cursor()

            print(f"Username: {username}")
            print(f"Password: {password}")

            sql_query = "SELECT id, rol_user, cod_vend FROM usuarios WHERE documento = %s AND password = %s"
            cursor.execute(sql_query, (username, password))
            user = cursor.fetchone()

            print(f"User found: {user}")

            if user:
                session['user_id'] = user[0]
                session['rol'] = user[1]
                session['cod_vend'] = user[2]
                # Verificar que la sesión se está guardando
                print(f"Session user_id: {session.get('user_id')}")
                print(f"Session rol: {session.get('rol')}")
                print(f"Session cod_vend: {session.get('cod_vend')}")

                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Usuario o contraseña incorrectos.")
        except Exception as e:
            print(f"Error during login: {e}")
            return render_template('login.html', error=f"Ocurrió un error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()
    return render_template('login.html') #login.html

@app.route('/')
def index():
    if 'user_id' in session: #username
        # Renderizar la plantilla con el nombre de usuario en el contexto
        return render_template('index.html', user_id=session['user_id'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Cerrar sesión
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('rol_user', None)
    session.pop('cod_vend', None)
    return redirect(url_for('login'))

@app.route('/procesar', methods=['POST'])
def procesar():
    #if 'username' not in session:
    #    return redirect(url_for('login'))
    data = request.get_json()
    nombre = data.get('nombre', '')
    cod_vend = data.get('cod_vend', '')

    if not nombre and cod_vend:
        return jsonify({'error': 'Nro Ruta no proporcionado'}), 400
    try:
        # Configuración de la conexión a la base de datos
        dsn = 'HANA_DSN'
        usuario = 'USERBRU'
        contrasena = 'Bru.Log@2024.'
        conexion = pyodbc.connect(f'DSN={dsn};UID={usuario};PWD={contrasena}')
        cursor = conexion.cursor()
        # Definir la consulta SQL
        nroreparto = nombre  # Usar el valor del nombre como parámetro en la consulta
        
        sql_query = """
             SELECT bs."CodigoCliente",
                    CAST(IFNULL(bs."Cliente", bs."NombreFantasia") AS NVARCHAR) AS Nombre,
                    bs."NroReferenciaOV",
                    bs."MontoTotalOV",
                    bs."MontoTotalFA",
                    bs."FechaEntrega"
               FROM BRUMADO_MIGRA."BruPedidoBruShopDetalle" bs 
              WHERE bs."Fecha" = ?
                AND (bs."CodigoVendedor" = ?
                 OR  -1 = -1)
              GROUP BY bs."CodigoCliente",
                       CAST(IFNULL(bs."Cliente", bs."NombreFantasia") AS NVARCHAR),
                       bs."NroReferenciaOV",
                       bs."MontoTotalOV",
                       bs."MontoTotalFA",
                       bs."FechaEntrega"
        """
        query_result = cursor.execute(sql_query, nroreparto, cod_vend)
        resultados = []
        for fila in query_result:
            resultados.append({
                'Codigo': fila[0],
                'Nombre': fila[1],
                'NroReferenciaOV': fila[2],
                'MontoTotalOV': fila[3],
                'MontoTotalFA': fila[4],
                'Fecha': fila[5]
            })

        print(resultados)
        return jsonify({'resultados': resultados})
        #return jsonify({'resultados': resultados, 'resultados2': resultados2})     
    except pyodbc.Error as e:
        # Manejar errores específicos de la base de datos
        print(f'Error de la base de datos: {str(e)}')
        return jsonify({'error': 'Error en la base de datos, consulte el log para más detalles'}), 500
    except Exception as e:
        # Manejar cualquier otro error
        print(f'Error general: {str(e)}')
        return jsonify({'error': 'Ocurrió un error en el servidor'}), 500
    finally:
        # Asegurar que la conexión se cierre
        try:
            cursor.close()
            conexion.close()
        except:
            pass  # En caso de que cerrar la conexión falle, lo ignoramos.

@app.route('/detalle_ovfa')
def detalle_ovfa():
    dsn = 'HANA_DSN'
    usuario = 'USERBRU'
    contrasena = 'Bru.Log@2024.'
    conexion = pyodbc.connect(f'DSN={dsn};UID={usuario};PWD={contrasena}')
    cursor = conexion.cursor()

    # Obtener parámetro de la URL
    vreferencia = request.args.get('vNroReferenciaOV')
    if not vreferencia:
        return "Referencia no proporcionada.", 400

    # Consulta SQL
    query1 = """
        SELECT bs."CodigoArticulo", 
               bs."DescripcionArticulo", 
               bs."CantidadOV", 
               bs."UnidadMedidaOV", 
               bs."PrecioOV", 
               bs."SubtotalOV",
               bs."Status"
          FROM BRUMADO_MIGRA."BruPedidoBruShopDetalle" bs
         WHERE bs."NroReferenciaOV" = ?
    """
    query2 = """
        SELECT bsh."CodigoArticulo", 
               bsh."DescripcionArticulo", 
               bsh."CantidadFA", 
               bsh."UnidadMedidaFA", 
               bsh."PrecioFA", 
               bsh."SubtotalFA",
               bsh."NroFactura"
          FROM BRUMADO_MIGRA."BruPedidoBruShopDetalle" bsh
         WHERE bsh."NroReferenciaFA" = ?
    """
    try:
        # Ejecutar la consulta
        query_result = cursor.execute(query1, vreferencia)
        resultados = []
        for fila in query_result:
            resultados.append({
                'CodigoArticulo': fila[0],
                'Descripcion': fila[1],
                'Cantidad': f"{fila[2]:,.0f}",
                'UnidadMedida': fila[3],
                'Precio': f"{fila[4]:,.0f}",  # Formato de precio
                'SubTotal': f"{fila[5]:,.0f}",  # Formato de subtotal
                'Status': fila[6]
            })
        print(resultados)

        query_result2 = cursor.execute(query2, vreferencia)
        resultados2 = []
        for fila in query_result2:
            resultados2.append({
                'CodigoArticulo': fila[0],
                'Descripcion': fila[1],
                'Cantidad': f"{fila[2]:,.0f}",
                'UnidadMedida': fila[3],
                'Precio': f"{fila[4]:,.0f}",  # Formato de precio
                'SubTotal': f"{fila[5]:,.0f}",  # Formato de subtotal
                'NroFactura': fila[6]
            })
        print(resultados2)

    except pyodbc.Error as e:
        print("Error ejecutando la consulta:", e)
        return "Error al obtener los datos.", 500
    finally:
        # Cerrar la conexión
        cursor.close()
        conexion.close()

    # Renderizar plantilla con resultados
    return render_template('detalle_ovfa.html', resultados=resultados, resultados2=resultados2)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)

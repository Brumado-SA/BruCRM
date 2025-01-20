from flask import abort, Blueprint, render_template, request, redirect, url_for, g
from functools import wraps

from helpers.verificador_acceso import *

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets', methods=['GET'])
def list_tickets():
    acceso = verificar_acceso(['admin', 'user'])
    if acceso:
        return acceso
    tickets = fetch_tickets()
    return render_template('ticket_list.html', tickets=tickets)

def fetch_tickets():
    try:
        with conectar() as coneccion:
            with coneccion.cursor() as cursor:
                query = """
                select tk.id, tk.creator_id, tk.client_id, tk.title, tk.description, tc.name as category, ts.name as status, tp.name as priority, tk.created_at from tickets tk
	                join ticket_categories tc on tk.category_id = tc.id
	                join ticket_status ts on tk.status_id = ts.id
	                join ticket_priorities tp on tk.status_id = tp.id
                """
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                tickets = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        # Manejar la excepción de conexión a la base de datos
        print(f"Error al conectar a la base de datos: {e}")
        abort(500, description="An error occurred while fetching tickets.")
    
    return tickets
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
    ticket_statuses = list_of_status()
    ticket_categories = list_of_categories()
    ticket_priorities = list_of_priorities()
    return render_template('ticket_list.html', tickets=tickets, statuses=ticket_statuses, categories=ticket_categories, priorities=ticket_priorities)

@tickets_bp.route('tickets/search', methods=['GET'])
def tickets_search():
    data = request.get_json()
    search_terms = data.get('search_term')
    if search_terms:
        tickets = search_tickets(search_terms)
    else:
        tickets = fetch_tickets()


# SQL RELATED FUNCTIONS
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

def search_tickets(search_terms):
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

def list_of_status():
    try:
        with conectar() as coneccion:
            with coneccion.cursor() as cursor:
                query = """
                select * from ticket_status
                """
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                ticket_statuses = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        # Manejar la excepción de conexión a la base de datos
        print(f"Error al conectar a la base de datos: {e}")
        abort(500, description="An error occurred while fetching tickets.")
    return ticket_statuses

def list_of_categories():
    try:
        with conectar() as coneccion:
            with coneccion.cursor() as cursor:
                query = """
                select * from ticket_categories
                """
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                ticket_categories = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        # Manejar la excepción de conexión a la base de datos
        print(f"Error al conectar a la base de datos: {e}")
        abort(500, description="An error occurred while fetching tickets.")
    return ticket_categories

def list_of_priorities():
    try:
        with conectar() as coneccion:
            with coneccion.cursor() as cursor:
                query = """
                select * from ticket_priorities
                """
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                ticket_priorities = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        # Manejar la excepción de conexión a la base de datos
        print(f"Error al conectar a la base de datos: {e}")
        abort(500, description="An error occurred while fetching tickets.")
    return ticket_priorities
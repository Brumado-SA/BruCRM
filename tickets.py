from flask import abort, Blueprint, render_template, request, redirect, url_for, g
from functools import wraps
import pdb

from helpers.verificador_acceso import *

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/', methods=['GET'])
def list_tickets():
    acceso = verificar_acceso(['admin', 'user'])
    if acceso:
        return acceso
    tickets = fetch_tickets()
    ticket_statuses = list_of_status()
    ticket_categories = list_of_categories()
    ticket_priorities = list_of_priorities()
    return render_template('ticket_list.html', tickets=tickets, statuses=ticket_statuses, categories=ticket_categories, priorities=ticket_priorities)

@tickets_bp.route('/search', methods=['POST'])
def search_form():
    acceso = verificar_acceso(['admin', 'user'])
    if acceso:
        return acceso

    # Obtener los valores de búsqueda del formulario
    search_terms = request.form.to_dict()

    
    # Realizar la búsqueda en la base de datos conforme  los términos de búsqueda
    tickets = search_tickets(search_terms)
    ticket_statuses = list_of_status()
    ticket_categories = list_of_categories()
    ticket_priorities = list_of_priorities()
    return render_template('ticket_list.html', tickets=tickets, statuses=ticket_statuses, categories=ticket_categories, priorities=ticket_priorities)


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
                base_query = """
                select tk.id, tk.creator_id, tk.client_id, tk.title, tk.description, tc.name as category, ts.name as status, tp.name as priority, tk.created_at from tickets tk
	                join ticket_categories tc on tk.category_id = tc.id
	                join ticket_status ts on tk.status_id = ts.id
	                join ticket_priorities tp on tk.status_id = tp.id
                    where 1=1
                """
                # Map dictionary keys to their corresponding database columns
                field_mapping = {
                    'status': 'tk.status_id',
                    'priority': 'tk.priority_id',
                    'category': 'tk.category_id',
                    'created_at': 'tk.created_at',
                    'cod_vend': 'tk.creator_id'
                }
                
                # Filter out empty values and build conditions
                conditions = []
                params = []
                for key, value in search_terms.items():
                    if value and value != '-1' and value != '':
                        if key == 'created_at':
                            conditions.append(f"DATE({field_mapping[key]}) = DATE('{value}')")
                            params.append(value)
                        else:
                            conditions.append(f"{field_mapping[key]} = {value}")
                        params.append(value)
               
                # Add conditions to query if they exist
                if conditions:
                    query = base_query + " AND " + " AND ".join(conditions)
                else:
                    query = base_query
                
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                tickets = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
    except Exception as e:
        # Manejar la excepción de conexión a la base de datos
        print(f"Error al conectar a la base de datos: {e}")
        abort(500, description="An error occurred while fetching tickets.")
    
    return tickets

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
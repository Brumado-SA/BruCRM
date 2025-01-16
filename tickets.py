from flask import Blueprint, render_template, request, redirect, url_for, g
from functools import wraps

from helpers.verificador_acceso import verificar_acceso

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets', methods=['GET'])
def list_tickets():
    acceso = verificar_acceso(['admin', 'user'])
    if acceso:
        return acceso
    
    return render_template('ticket_list.html')



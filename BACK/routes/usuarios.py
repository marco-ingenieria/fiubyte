from flask import Blueprint, jsonify, request
import json
from services.usuarios import listar_usuarios, chequear_usuario, crear_usuario, eliminar_usuario
from utils import (construir_error)

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/', methods=['GET'])
def get_usuarios():
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    return listar_usuarios(limit, offset)

@usuarios_bp.route('/login', methods=['POST'])
def post_login():
    body = request.get_json()
    nombre = body.get('nombre')
    contrasenia = body.get('contrasenia')
    return chequear_usuario(nombre, contrasenia)

@usuarios_bp.route('/', methods=['POST'])
def post_usuario():
    body = request.get_json()
    if not body or len(body) == 0:
        return construir_error(400, "Datos vacíos")
    nombre = body.get('nombre')
    contrasenia = body.get('contrasenia')
    if not nombre or not contrasenia:
        return construir_error(400, "Faltan campos obligatorios")

    return crear_usuario(nombre, contrasenia)

@usuarios_bp.route('/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    return eliminar_usuario(id)
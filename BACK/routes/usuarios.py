from flask import Blueprint, jsonify, request
import json
from services.usuarios import listar_usuarios, chequear_usuario
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
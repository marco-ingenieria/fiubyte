from flask import Blueprint, jsonify, request
import json
from ..services import (listar_alumnos, buscar_alumno, crear_alumno, actualizar_alumno, eliminar_alumno, eliminar_alumno_permanente)
from ..utils import (construir_error)

alumnos_bp = Blueprint('alumnos', __name__)



@alumnos_bp.route('/', methods=['GET'])
def get_alumnos():
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    alumnos = listar_alumnos(limit, offset)

    return alumnos



@alumnos_bp.route('/<int:id', methods=['GET'])
def get_alumno(id):
    alumno = buscar_alumno(id)

    return alumno



@alumnos_bp.route('/csv', methods=['POST'])
def post_alumnos_csv():
    pass



@alumnos_bp.route('/', methods=['POST'])
def post_alumno():
    body = request.get_json()

    padron      = body.get('padron')
    nombre      = body.get('nombre')
    apellido    = body.get('apellido')
    email       = body.get('email')

    if len(body) == 0:
        return construir_error("Datos vacíos", 400)
    if not padron or not nombre or not apellido or not email:
        return construir_error("Faltan campos obligatorios", 400)
    
    alumno = crear_alumno(body)
    return alumno



@alumnos_bp.route('/<int:id>', methods=['PATCH'])
def patch_alumno(id):
    body = request.get_json()

    if len(body) == 0:
        return construir_error("Datos vacíos", 400)
    
    alumno = actualizar_alumno(body, id)
    return alumno



@alumnos_bp.route('/<int:id>', methods=['DELETE'])
def delete_alumno_virtual(id):
    return eliminar_alumno()



@alumnos_bp.route('/perma/<int:id>', methods=['DELETE'])
def delete_alumno_virtual(id):
    return eliminar_alumno_permanente()

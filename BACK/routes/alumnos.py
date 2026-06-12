from flask import Blueprint, jsonify, request
import json
from services.alumnos import (listar_alumnos, buscar_alumno, crear_alumno, actualizar_alumno, eliminar_alumno, eliminar_alumno_permanente, crear_alumnos_csv)
from utils import (construir_error)

alumnos_bp = Blueprint('alumnos', __name__)



@alumnos_bp.route('/', methods=['GET'])
def get_alumnos():
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    alumnos = listar_alumnos(limit, offset, base_url)

    return alumnos



@alumnos_bp.route('/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = buscar_alumno(id)

    return alumno



@alumnos_bp.route('/csv', methods=['POST'])
def post_alumnos_csv():
    listado_alumnos = request.files.get('alumnos')
    if not listado_alumnos:
        return construir_error(400, "Falta archivo")
    if not listado_alumnos.filename.endswith(".csv"):
        return construir_error(400, "El listado debe ser un archivo .csv")
    
    return crear_alumnos_csv(listado_alumnos)

@alumnos_bp.route('/', methods=['POST'])
def post_alumno():
    body = request.get_json()

    padron      = body.get('padron')
    nombre      = body.get('nombre')
    apellido    = body.get('apellido')
    email       = body.get('email')
    #abandono es 0 por default, no entra en POST

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    if not padron or not nombre or not apellido or not email:
        return construir_error(400, "Faltan campos obligatorios")
    
    alumno = crear_alumno(body)
    return alumno



@alumnos_bp.route('/<int:id>', methods=['PATCH'])
def patch_alumno(id):
    body = request.get_json()

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    
    alumno = actualizar_alumno(body, id)
    return alumno



@alumnos_bp.route('/<int:id>', methods=['DELETE'])
def delete_alumno_virtual(id):
    return eliminar_alumno(id)



@alumnos_bp.route('/perma/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    return eliminar_alumno_permanente(id)

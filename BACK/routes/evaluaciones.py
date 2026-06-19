from flask import Blueprint, jsonify, request
import json
from services.evaluaciones import (listar_evaluaciones,listar_evaluaciones_alumno, buscar_evaluacion, crear_evaluacion, actualizar_evaluacion, eliminar_evaluacion, eliminar_evaluacion_permanente)
from utils import (construir_error)
from constants import (TIPOS_EVAL)

evaluaciones_bp = Blueprint('evaluaciones', __name__)



@evaluaciones_bp.route('/', methods=['GET'])
def get_evaluaciones():
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    evaluaciones = listar_evaluaciones(limit, offset, base_url)

    return evaluaciones



@evaluaciones_bp.route('/<int:id>', methods=['GET'])
def get_evaluacion(id):
    evaluacion = buscar_evaluacion(id)

    return evaluacion



@evaluaciones_bp.route('/', methods=['POST'])
def post_evaluacion():
    body = request.get_json()

    tipo        = body.get('tipo')
    nombre      = body.get('nombre')
    materia     = body.get('id_materia')

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    if not tipo or not nombre or not materia:
        return construir_error(400, "Faltan campos obligatorios")
    if tipo not in TIPOS_EVAL:
        return construir_error(400, f"Tipo debe ser uno de estos valores: {', '.join([tipo for tipo in TIPOS_EVAL])}")
    
    evaluacion = crear_evaluacion(body)
    return evaluacion



@evaluaciones_bp.route('/<int:id>', methods=['PATCH'])
def patch_evaluacion(id):
    body = request.get_json()

    tipo        = body.get('tipo')

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    if tipo and tipo not in TIPOS_EVAL:
        return construir_error(400, f"Tipo debe ser uno de estos valores: {', '.join([tipo for tipo in TIPOS_EVAL])}")
    
    evaluacion = actualizar_evaluacion(body, id)
    return evaluacion



@evaluaciones_bp.route('/<int:id>', methods=['DELETE'])
def delete_evaluacion_virtual(id):
    return eliminar_evaluacion(id)



@evaluaciones_bp.route('/perma/<int:id>', methods=['DELETE'])
def delete_evaluacion(id):
    return eliminar_evaluacion_permanente(id)

@evaluaciones_bp.route('/del-alumno/<int:padron>', methods=['GET'])
def get_evaluaciones_alumno(padron):
    return listar_evaluaciones_alumno(padron)

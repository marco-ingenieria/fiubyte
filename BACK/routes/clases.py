from flask import Blueprint, jsonify, request
import json
from services.clases import (listar_clases, buscar_clase, crear_clase, actualizar_clase, eliminar_clase, eliminar_clase_permanente)
from utils import (construir_error, validar_fecha)

clases_bp = Blueprint('clases', __name__)


@clases_bp.route('/', methods=['GET'])
def get_clases():
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    clases = listar_clases(limit, offset, base_url)

    return clases



@clases_bp.route('/<int:id>', methods=['GET'])
def get_clase(id):
    clase = buscar_clase(id)

    return clase



@clases_bp.route('/', methods=['POST'])
def post_clase():
    body = request.get_json()

    profesores      = body.get('profesores')
    fecha           = body.get('fecha')
    
    #materia         = body.get('id_materia')

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    if not profesores or not fecha:
        return construir_error(400, "Faltan campos obligatorios")
    if not isinstance(profesores, list):
        return construir_error(400, "Profesores debe ser una lista")
    if not validar_fecha(fecha):
        return construir_error(400, "Fecha inválida")

    clase = crear_clase(body)
    return clase



@clases_bp.route('/<int:id>', methods=['PATCH'])
def patch_clase(id):
    body = request.get_json()

    profesores      = body.get('profesores')
    fecha           = body.get('fecha')

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    if profesores and not isinstance(profesores, list):
        return construir_error(400, "Profesores debe ser una lista")    
    if fecha and not validar_fecha(fecha):
        return construir_error(400, "Fecha inválida")
    
    clase = actualizar_clase(body, id)
    return clase



@clases_bp.route('/<int:id>', methods=['DELETE'])
def delete_clase_virtual(id):
    return eliminar_clase(id)



@clases_bp.route('/perma/<int:id>', methods=['DELETE'])
def delete_clase(id):
    return eliminar_clase_permanente(id)

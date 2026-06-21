from flask import Blueprint, jsonify, request
from services.materias import (listar_materias, crear_materia, obtener_materia,
                               actualizar_materia, eliminar_materia, obtener_estadisticas_pdf)
from utils import construir_error
import json
from flask_jwt_extended import jwt_required, get_jwt_identity

materias_bp = Blueprint('materias', __name__)

@materias_bp.route("/", methods=['GET'])
def get_materias():
    
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    return listar_materias(base_url, limit, offset)

@materias_bp.route("/<int:id>", methods=['GET'])
def get_materia(id):
    if id <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo")
    
    return obtener_materia(id)

@materias_bp.route("/pdf", methods=['GET'])
def get_estadisticas_materia_pdf():
    pdf = obtener_estadisticas_pdf()

    return pdf


@materias_bp.route("/", methods=['POST'])
@jwt_required()
def post_materia():

    data=request.get_json()
    nombre = data.get('nombre_materia')
    cuatrimestre = data.get('cuatrimestre')
    anio = data.get('anio')

    if not nombre:
        return construir_error(400, "No se ha especificado ningun valor para 'nombre_materia'") 
    
    if not isinstance(cuatrimestre, int) or (cuatrimestre != 1 and cuatrimestre!=2):
        return construir_error(400, "'cuatrimestre' debe ser el numero de valor 1 o de valor 2")
   
    if not isinstance(anio, int) or not (anio >= 2000 and anio <= 2100):
        return construir_error(400, "'anio' debe ser el anio entre el rango [2000, 2100]")

    return crear_materia(nombre, cuatrimestre, anio)

@materias_bp.route("/<int:id>", methods=['PATCH'])
@jwt_required()
def patch_materia(id):

    if id <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo")

    body=request.get_json()

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    
    return actualizar_materia(id, body)

@materias_bp.route("/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_materia(id):
    if id <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo")
    
    return eliminar_materia(id)
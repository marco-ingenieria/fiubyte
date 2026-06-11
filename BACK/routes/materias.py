from flask import Blueprint, jsonify, request
from services.materias import (listar_materias, crear_materia)
from utils import construir_error
import json



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



@materias_bp.route("/", methods=['POST'])
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
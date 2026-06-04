from flask import Blueprint, jsonify, request
from services.grupos import (listar_grupos, obtener_grupo, crear_grupo)
from utils import construir_error
import json


grupos_bp = Blueprint('grupos', __name__)


@grupos_bp.route("/", methods=['GET'])
def get_grupos():

    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    return listar_grupos(base_url, limit, offset)



@grupos_bp.route("/<int:id>", methods=['GET'])
def get_grupo(id):

    return obtener_grupo(id)


@grupos_bp.route("/", methods=['POST'])
def post_grupo():

    data=request.get_json()
    nombre = data.get('nombre')

    if not nombre:
        return (jsonify("No se ha especificado ningun nombre"), 400) 
    
    return crear_grupo(nombre)



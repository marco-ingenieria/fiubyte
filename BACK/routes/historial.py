from flask import Blueprint, jsonify, request
import json
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.historial import historial_completo, historial_usuario, eliminar_registro
from utils import (construir_error)

historiales_bp = Blueprint('historiales', __name__)

@historiales_bp.route('/', methods=['GET'])
def get_historiales():
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    historial = historial_completo(limit, offset, base_url)

    return historial

@historiales_bp.route('/<int:id_user>', methods=['GET'])
def get_historial_usuario(id_user):
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    historial = historial_usuario(limit, offset, base_url, id_user)

    return historial

@historiales_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_registro(id):
    return eliminar_registro(id)
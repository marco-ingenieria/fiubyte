from flask import Blueprint, jsonify, request
from services.grupos import listar_grupos
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


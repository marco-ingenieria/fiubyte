from flask import Blueprint, request
from services.notas import listar_notas, listar_notas_padron, listar_notas_evaluacion, crear_nota, listar_planilla_notas
from utils import construir_error
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.historial import registrar

notas_bp = Blueprint('notas', __name__)

@notas_bp.route('/', methods=['GET'])
def get_notas():
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)
    padron = request.args.get('padron', type=int)
    id_evaluacion = request.args.get('id_evaluacion', type=int)

    if limit is None or limit < 0:
        limit = 10
    if offset is None or offset < 0:
        offset = 0

    if padron:
        return listar_notas_padron(limit, offset, padron)
    if id_evaluacion:
        return listar_notas_evaluacion(limit, offset, id_evaluacion)
    return listar_notas(limit, offset)

@notas_bp.route('/', methods=['POST'])
@jwt_required()
@registrar("Cargado una nota")
def post_nota():
    body = request.get_json()

    if not body or len(body) == 0:
        return construir_error(400, "Datos vacíos")

    nota = body.get('nota')
    padron = body.get('padron')
    id_evaluacion = body.get('id_evaluacion')

    if not nota or not padron or not id_evaluacion:
        return construir_error(400, "Faltan campos obligatorios")

    return crear_nota(padron, id_evaluacion, nota)



@notas_bp.route('/planilla', methods=['GET'])
#@jwt_required()
def get_planilla():
    id_materia = request.args.get('id_materia', type=int)
    if not id_materia:
        return construir_error(400, "Falta id_materia")
    return listar_planilla_notas(id_materia)
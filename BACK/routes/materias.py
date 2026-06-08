from flask import Blueprint, jsonify, request
from utils import construir_error
import json



materias_bp = Blueprint('materias', __name__)


@materias_bp.route("/", methods=['GET'])
def get_materias():
    return "hola"

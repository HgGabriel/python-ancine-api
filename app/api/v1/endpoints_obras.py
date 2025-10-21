# app/api/v1/endpoints_obras.py

from flask import Blueprint, jsonify, request
from app.services import obra_service # Importa o serviço

# Cria um novo Blueprint para este domínio
obras_bp = Blueprint('obras_bp', __name__)

@obras_bp.route('/pesquisa', methods=['GET'])
def get_obras_com_joins():
    """
    ENDPOINT PODEROSO: Busca 'obras' e automaticamente anexa
    os dados de 'paises_origem' (JOINs).
    """
    try:
        params = request.args.to_dict()
        data, pagination = obra_service.get_obras_com_join(params)
        
        return jsonify({ 'data': data, 'pagination': pagination })

    except Exception as e:
        print(f"Erro em /pesquisa (obras): {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500


@obras_bp.route('/estatisticas/por_tipo', methods=['GET'])
def get_stats_obras_por_tipo():
    """
    ENDPOINT DE AGREGAÇÃO (BI): Retorna a contagem de obras 
    agrupada por tipo, direto do banco.
    """
    try:
        data = obra_service.get_stats_obras_por_tipo()
        return jsonify(data)

    except Exception as e:
        print(f"Erro em /estatisticas/por_tipo: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500
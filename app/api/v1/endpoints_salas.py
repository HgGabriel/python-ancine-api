# app/api/v1/endpoints_salas.py

from flask import Blueprint, jsonify, request
# Importa o *serviço* que tem a lógica
from app.services import sala_service 

# Renomeia o Blueprint para ser mais específico
salas_bp = Blueprint('salas_bp', __name__)
# O CORS pode ser gerenciado globalmente no app/__init__.py

@salas_bp.route('/<string:table_name>', methods=['GET'])
def get_table_cursor(table_name):
    """
    ENDPOINT GENÉRICO: Busca dados de 'salas', 'complexos' ou 'exibidores'.
    """
    try:
        # 1. Pega os parâmetros da URL
        params = request.args.to_dict()
        
        # 2. Chama o SERVIÇO para fazer o trabalho
        data, pagination = sala_service.get_generic_table_data(table_name, params)
        
        # 3. Apenas retorna a resposta
        return jsonify({ 'data': data, 'pagination': pagination })

    except ValueError as e: # Captura o erro "Nome de tabela inválido"
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Erro em /data/{table_name}: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500
    
@salas_bp.route('/estatisticas/salas_por_uf', methods=['GET'])
def get_stats_salas_por_uf():
    """
    ENDPOINT DE AGREGAÇÃO (BI): Retorna a contagem de salas 
    agrupada por UF, direto do banco.
    """
    if supabase is None:
        return jsonify({'error': 'Serviço Supabase não está disponível.'}), 503
        
    try:
        # 'rpc' chama a função SQL que acabamos de criar
        response = supabase.rpc('contar_salas_por_uf').execute()
        
        return jsonify(response.data)

    except Exception as e:
        print(f"Erro em /estatisticas/salas_por_uf: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500

@salas_bp.route('/pesquisa', methods=['GET'])
def get_salas_com_joins():
    """
    ENDPOINT PODEROSO: Busca 'salas' com JOINs.
    """
    try:
        # 1. Pega os parâmetros
        params = request.args.to_dict()
        
        # 2. Chama o SERVIÇO
        data, pagination = sala_service.get_salas_com_join(params)
        
        # 3. Retorna a resposta
        return jsonify({ 'data': data, 'pagination': pagination })

    except Exception as e:
        print(f"Erro em /pesquisa-salas: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500
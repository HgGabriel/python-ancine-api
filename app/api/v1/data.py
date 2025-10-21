from flask import Blueprint, jsonify, request
from app.services.supabase_service import supabase # Importa seu cliente Supabase
from flask_cors import CORS
# Remova as importações do google.cloud.firestore

# --- Configuração do Blueprint ---
# (Se você refatorou, este pode ser 'salas_bp', 'obras_bp', etc.)
# (Vou manter 'data_bp' como no seu exemplo)
data_bp = Blueprint('data_bp', __name__)
CORS(data_bp)


@data_bp.route('/data/<string:table_name>', methods=['GET'])
def get_table_cursor(table_name):
    """
    ENDPOINT GENÉRICO Otimizado com Paginação Baseada em Cursor (Keyset).
    Agora inclui as novas tabelas.
    """
    if supabase is None:
        return jsonify({'error': 'Serviço Supabase não está disponível.'}), 503
        
    try:
        # 1. Validação simples do nome da tabela (ATUALIZADO)
        allowed_tables = [
            'exibidores', 'complexos', 'salas',
            'obras', 'paises_origem', 'filmagem_estrangeira'
            'distribuidoras', 'lancamentos'
        ]
        if table_name not in allowed_tables:
            return jsonify({'error': 'Nome de tabela inválido.'}), 400

        # 2. Parâmetros de paginação e limite
        limit = min(int(request.args.get('limit', 10)), 100)
        last_id = request.args.get('last_id') 
        
        # 3. Define a Chave Primária correta (ATUALIZADO)
        primary_key_map = {
            'exibidores': 'registro_exibidor',
            'complexos': 'registro_complexo',
            'salas': 'registro_sala',
            'obras': 'cpb',
            'paises_origem': 'id', # Chave SERIAL da tabela
            'distribuidoras': 'registro_distribuidora',
            'lancamentos': 'id' # Chave SERIAL da tabela
        }
        
        # O 'get' previne um erro se a tabela for válida
        # mas não estiver no mapa (embora devesse estar)
        primary_key_column = primary_key_map.get(table_name)
        if not primary_key_column:
             return jsonify({'error': 'Configuração de chave primária não encontrada.'}), 500

        # 4. Constrói a query base
        query_builder = supabase.table(table_name).select('*', count='exact')
        
        # 5. Constrói filtros dinâmicos
        filter_params = {k: v for k, v in request.args.items() 
                         if k not in ['limit', 'last_id']}
        
        for key, value in filter_params.items():
            if '.' not in key: 
                query_builder = query_builder.eq(key, value)
        
        # 6. Adiciona ordenação e cursor
        query_builder = query_builder.order(primary_key_column)
        if last_id:
            query_builder = query_builder.gt(primary_key_column, last_id)
        
        # 7. Busca (limit + 1) e executa
        response = query_builder.limit(limit + 1).execute()
        
        # 8. Processa os resultados
        docs_with_extra = response.data
        total_count = response.count
        has_next = len(docs_with_extra) > limit
        docs_for_page = docs_with_extra[:limit]
        data = docs_for_page
        
        # 9. Define o cursor
        next_cursor = None
        if has_next and docs_for_page:
            next_cursor = docs_for_page[-1].get(primary_key_column)
        
        return jsonify({
            'data': data,
            'pagination': {
                'total_filtered_count': total_count,
                'per_page': limit,
                'next_cursor': next_cursor, 
                'has_next': has_next
            }
        })

    except Exception as e:
        print(f"Erro geral na consulta: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500


@data_bp.route('/pesquisa-salas', methods=['GET'])
def get_salas_com_joins():
    """
    ENDPOINT PODEROSO (Salas): Busca 'salas' com JOINs
    em 'complexos' e 'exibidores'.
    """
    if supabase is None:
        return jsonify({'error': 'Serviço Supabase não está disponível.'}), 503
        
    try:
        # 1. Parâmetros
        limit = min(int(request.args.get('limit', 10)), 100)
        last_id = request.args.get('last_id')
        primary_key_column = 'registro_sala'

        # 2. Query com JOINs
        select_query = '*, complexos!inner(*, exibidores(*))'
        query_builder = supabase.table('salas').select(select_query, count='exact')
        
        # 3. Filtros
        filter_params = {k: v for k, v in request.args.items() 
                         if k not in ['limit', 'last_id']}
        
        for key, value in filter_params.items():
            query_builder = query_builder.eq(key, value)
        
        # 4. Paginação
        query_builder = query_builder.order(primary_key_column) 
        if last_id:
            query_builder = query_builder.gt(primary_key_column, last_id)
        
        # 5. Executa
        response = query_builder.limit(limit + 1).execute()
        
        # 6. Processa
        docs_with_extra = response.data
        total_count = response.count
        has_next = len(docs_with_extra) > limit
        docs_for_page = docs_with_extra[:limit]
        data = docs_for_page
        
        next_cursor = None
        if has_next and docs_for_page:
            next_cursor = docs_for_page[-1].get(primary_key_column)
        
        # 7. Retorna
        return jsonify({
            'data': data,
            'pagination': {
                'total_filtered_count': total_count,
                'per_page': limit,
                'next_cursor': next_cursor, 
                'has_next': has_next
            }
        })

    except Exception as e:
        print(f"Erro geral na consulta: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500

# --- NOVOS ENDPOINTS PARA OBRAS E ESTATÍSTICAS ---

@data_bp.route('/pesquisa-obras', methods=['GET'])
def get_obras_com_joins():
    """
    ENDPOINT PODEROSO (Obras): Busca 'obras' e automaticamente anexa
    a lista de 'paises_origem' (JOINs).
    """
    if supabase is None:
        return jsonify({'error': 'Serviço Supabase não está disponível.'}), 503
        
    try:
        # 1. Parâmetros
        limit = min(int(request.args.get('limit', 10)), 100)
        last_id = request.args.get('last_id')
        primary_key_column = 'cpb' # Chave primária da tabela 'obras'

        # 2. Query com JOINs
        # '*, paises_origem(*)' -> Traga tudo da obra E
        # uma lista de todos os 'paises_origem' relacionados.
        select_query = '*, paises_origem(*)'
        
        # 3. Filtros
        filter_params = {k: v for k, v in request.args.items() 
                         if k not in ['limit', 'last_id']}

        # Se houver um filtro na tabela 'paises_origem',
        # forçamos um 'inner join' para que apenas as obras que 
        # correspondem ao país sejam retornadas.
        if any(key.startswith('paises_origem.') for key in filter_params):
            select_query = '*, paises_origem!inner(*)'

        query_builder = supabase.table('obras').select(select_query, count='exact')

        for key, value in filter_params.items():
            query_builder = query_builder.eq(key, value)
        
        # 4. Paginação
        query_builder = query_builder.order(primary_key_column)
        if last_id:
            query_builder = query_builder.gt(primary_key_column, last_id)
        
        # 5. Executa
        response = query_builder.limit(limit + 1).execute()
        
        # 6. Processa
        docs_with_extra = response.data
        total_count = response.count
        has_next = len(docs_with_extra) > limit
        docs_for_page = docs_with_extra[:limit]
        data = docs_for_page
        
        next_cursor = None
        if has_next and docs_for_page:
            next_cursor = docs_for_page[-1].get(primary_key_column)
        
        # 7. Retorna
        return jsonify({
            'data': data,
            'pagination': {
                'total_filtered_count': total_count,
                'per_page': limit,
                'next_cursor': next_cursor, 
                'has_next': has_next
            }
        })

    except Exception as e:
        print(f"Erro geral na consulta: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500


@data_bp.route('/estatisticas/salas_por_uf', methods=['GET'])
def get_stats_salas_por_uf():
    """
    ENDPOINT DE AGREGAÇÃO (BI): Retorna a contagem de salas 
    agrupada por UF, direto do banco.
    (Requer a função SQL 'contar_salas_por_uf' no Supabase)
    """
    if supabase is None:
        return jsonify({'error': 'Serviço Supabase não está disponível.'}), 503
        
    try:
        response = supabase.rpc('contar_salas_por_uf').execute()
        return jsonify(response.data)

    except Exception as e:
        print(f"Erro em /estatisticas/salas_por_uf: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500


@data_bp.route('/estatisticas/obras_por_tipo', methods=['GET'])
def get_stats_obras_por_tipo():
    """
    ENDPOINT DE AGREGAÇÃO (BI): Retorna a contagem de obras 
    agrupada por tipo, direto do banco.
    (Requer a função SQL 'contar_obras_por_tipo' no Supabase)
    """
    if supabase is None:
        return jsonify({'error': 'Serviço Supabase não está disponível.'}), 503
        
    try:
        response = supabase.rpc('contar_obras_por_tipo').execute()
        return jsonify(response.data)

    except Exception as e:
        print(f"Erro em /estatisticas/obras_por_tipo: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500


@data_bp.route('/estatisticas/market_share', methods=['GET'])
def get_stats_market_share():
    try:
        response = supabase.rpc('calcular_market_share_nacional').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@data_bp.route('/estatisticas/ranking_distribuidoras', methods=['GET'])
def get_stats_ranking_distribuidoras():
    try:
        response = supabase.rpc('ranking_distribuidoras').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
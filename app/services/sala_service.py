# app/services/sala_service.py

from app.services.supabase_service import supabase

def get_generic_table_data(table_name: str, params: dict):
    """
    Busca dados de uma tabela genérica com filtros e paginação.
    (Esta é a lógica do seu endpoint /data/<string:table_name>)
    """
    if supabase is None:
        raise Exception("Serviço Supabase não está disponível.")

    # 1. Validação
    primary_key_map = {
        'exibidores': 'registro_exibidor',
        'complexos': 'registro_complexo',
        'salas': 'registro_sala'
    }
    if table_name not in primary_key_map:
        raise ValueError("Nome de tabela inválido.")
    
    primary_key_column = primary_key_map[table_name]

    # 2. Parâmetros
    limit = min(int(params.get('limit', 10)), 100)
    last_id = params.get('last_id')

    # 3. Constrói a query
    query_builder = supabase.table(table_name).select('*', count='exact')
    
    filter_params = {k: v for k, v in params.items() if k not in ['limit', 'last_id']}
    for key, value in filter_params.items():
        if '.' not in key:
            query_builder = query_builder.eq(key, value)
    
    query_builder = query_builder.order(primary_key_column)
    if last_id:
        query_builder = query_builder.gt(primary_key_column, last_id)
    
    # 4. Executa
    response = query_builder.limit(limit + 1).execute()
    
    # 5. Processa e Retorna os dados
    docs_with_extra = response.data
    total_count = response.count
    
    has_next = len(docs_with_extra) > limit
    docs_for_page = docs_with_extra[:limit]
    
    next_cursor = None
    if has_next and docs_for_page:
        next_cursor = docs_for_page[-1].get(primary_key_column)
    
    pagination_info = {
        'total_filtered_count': total_count,
        'per_page': limit,
        'next_cursor': next_cursor, 
        'has_next': has_next
    }
    
    return docs_for_page, pagination_info


def get_salas_com_join(params: dict):
    """
    Busca salas com JOIN em complexos e exibidores.
    (Esta é a lógica do seu endpoint /pesquisa-salas)
    """
    if supabase is None:
        raise Exception("Serviço Supabase não está disponível.")

    # 1. Parâmetros
    limit = min(int(params.get('limit', 10)), 100)
    last_id = params.get('last_id')
    primary_key_column = 'registro_sala'
    
    # 2. Query com JOINs
    select_query = '*, complexos!inner(*, exibidores(*))'
    query_builder = supabase.table('salas').select(select_query, count='exact')
    
    # 3. Filtros
    filter_params = {k: v for k, v in params.items() if k not in ['limit', 'last_id']}
    for key, value in filter_params.items():
        query_builder = query_builder.eq(key, value)
    
    # 4. Paginação
    query_builder = query_builder.order(primary_key_column)
    if last_id:
        query_builder = query_builder.gt(primary_key_column, last_id)
    
    # 5. Executa
    response = query_builder.limit(limit + 1).execute()
    
    # 6. Processa e Retorna
    docs_with_extra = response.data
    total_count = response.count
    
    has_next = len(docs_with_extra) > limit
    docs_for_page = docs_with_extra[:limit]
    
    next_cursor = None
    if has_next and docs_for_page:
        next_cursor = docs_for_page[-1].get(primary_key_column)
    
    pagination_info = {
        'total_filtered_count': total_count,
        'per_page': limit,
        'next_cursor': next_cursor, 
        'has_next': has_next
    }
    
    return docs_for_page, pagination_info
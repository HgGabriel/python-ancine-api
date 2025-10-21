# app/services/obra_service.py

from app.services.supabase_service import supabase

def get_obras_com_join(params: dict):
    """
    Busca obras com JOIN em paises_origem.
    Permite filtros dinâmicos.
    """
    if supabase is None:
        raise Exception("Serviço Supabase não está disponível.")

    # 1. Parâmetros de paginação
    limit = min(int(params.get('limit', 10)), 100)
    last_id = params.get('last_id')
    primary_key_column = 'cpb' # Chave primária da tabela 'obras'
    
    # 2. Query com JOINs
    # '*, paises_origem(*)' -> Traga tudo da obra E
    # uma lista de todos os 'paises_origem' relacionados.
    select_query = '*, paises_origem(*)'
    
    # 3. Filtros
    filter_params = {k: v for k, v in params.items() if k not in ['limit', 'last_id']}
    
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


def get_stats_obras_por_tipo():
    """Chama a função RPC 'contar_obras_por_tipo' do banco."""
    if supabase is None:
        raise Exception("Serviço Supabase não está disponível.")
        
    response = supabase.rpc('contar_obras_por_tipo').execute()
    return response.data
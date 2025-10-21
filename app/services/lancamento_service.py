from app.services.supabase_service import supabase

def get_lancamentos_com_join(params: dict):
    """
    Busca Lançamentos com JOIN em Distribuidoras e Obras.
    """
    if supabase is None:
        raise Exception("Serviço Supabase não está disponível.")

    limit = min(int(params.get('limit', 10)), 100)
    last_id = params.get('last_id')
    primary_key_column = 'id' # Chave SERIAL da tabela 'lancamentos'
    
    # Query: Pega tudo de Lançamentos,
    # Traz os dados da Distribuidora (obrigatório)
    # Traz os dados da Obra (opcional, pois pode ser filme estrangeiro)
    select_query = '*, distribuidoras!inner(*), obras(*)'
    
    query_builder = supabase.table('lancamentos').select(select_query, count='exact')
    
    filter_params = {k: v for k, v in params.items() if k not in ['limit', 'last_id']}
    for key, value in filter_params.items():
        query_builder = query_builder.eq(key, value)
    
    # Ordena por ID (data de inserção) ou data de lançamento
    query_builder = query_builder.order('data_lancamento', desc=True)
    if last_id:
        # Cursor por ID ainda é mais seguro que por data
        query_builder = query_builder.order(primary_key_column)
        query_builder = query_builder.gt(primary_key_column, last_id)
    
    response = query_builder.limit(limit + 1).execute()
    
    # Processa e Retorna
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
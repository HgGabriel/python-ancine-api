from app.services.supabase_service import supabase

# Você está tentando importar esta classe
class FilmagemService:
    
    def __init__(self):
        if supabase is None:
            raise Exception("Serviço Supabase não está disponível.")
        self.supabase = supabase

    def get_filmagens_estrangeiras(self, params: dict):
        """
        Busca dados da tabela 'filmagem_estrangeira' com filtros e paginação.
        """
        # 1. Parâmetros de paginação
        limit = min(int(params.get('limit', 10)), 100)
        last_id = params.get('last_id')
        primary_key_column = 'id_filmagem' # Chave da tabela

        # 2. Constrói a query
        query_builder = self.supabase.table('filmagem_estrangeira').select('*', count='exact')

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

        # 6. Processa e Retorna (Lógica de paginação copiada dos outros serviços)
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

# Cria uma instância única para ser importada
filmagem_service_instance = FilmagemService()
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
    Acesso direto a tabelas individuais com paginação
    ---
    tags:
      - Acesso Direto
    summary: Busca dados de uma tabela específica sem relacionamentos.
    description: >
      Endpoint genérico que permite acesso direto aos dados de qualquer tabela do sistema.
      Retorna dados "planos" (sem JOINs) com paginação baseada em cursor para performance otimizada.
      Ideal para análises que precisam apenas dos dados de uma entidade específica.
    parameters:
      - in: path
        name: table_name
        required: true
        schema:
          type: string
          enum: ['exibidores', 'complexos', 'salas', 'obras', 'paises_origem', 'distribuidoras', 'lancamentos']
        description: Nome da tabela a ser consultada.
      - in: query
        name: limit
        schema:
          type: integer
          default: 10
          maximum: 100
        description: Número de itens por página.
      - in: query
        name: last_id
        schema:
          type: string
        description: Cursor da página anterior (usar a chave primária do último item).
    responses:
      200:
        description: Lista paginada de registros da tabela solicitada.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: object
                    description: Estrutura varia conforme a tabela solicitada.
                pagination:
                  type: object
                  properties:
                    total_filtered_count:
                      type: integer
                    per_page:
                      type: integer
                    next_cursor:
                      type: string
                    has_next:
                      type: boolean
      400:
        description: Nome de tabela inválido.
      500:
        description: Erro interno do servidor.
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
    Busca detalhada de Salas de Cinema
    ---
    tags:
      - Exibição
    summary: Busca salas de cinema com dados aninhados de complexos e exibidores.
    description: >
      Retorna uma lista paginada de salas de cinema. Cada sala na resposta contém
      um objeto aninhado `complexos`, que por sua vez contém um objeto aninhado `exibidores`.
      Permite filtros avançados em campos das tabelas relacionadas, ideal para análises
      geográficas e de infraestrutura de exibição.
    parameters:
      - in: query
        name: limit
        schema:
          type: integer
          default: 10
          maximum: 100
        description: Número de itens por página.
      - in: query
        name: last_id
        schema:
          type: string
        description: O cursor da página anterior (usar o `registro_sala`).
      - in: query
        name: situacao_sala
        schema:
          type: string
          enum: ['Em Funcionamento', 'Fechado', 'Em Construção', 'Reformando']
          example: 'Em Funcionamento'
        description: Filtra pela situação operacional da sala.
      - in: query
        name: tipo_tela
        schema:
          type: string
          example: '2D'
        description: Filtra por tecnologia de projeção (2D, 3D, IMAX, etc.).
      - in: query
        name: tipo_som
        schema:
          type: string
          example: 'DOLBY DIGITAL'
        description: Filtra por sistema de áudio.
      - in: query
        name: complexos.uf_complexo
        schema:
          type: string
          example: 'SP'
        description: (Filtro Aninhado) Filtra por salas localizadas num estado (UF) específico.
      - in: query
        name: complexos.municipio_complexo
        schema:
          type: string
          example: 'São Paulo'
        description: (Filtro Aninhado) Filtra por salas localizadas numa cidade específica.
      - in: query
        name: complexos.exibidores.nome_grupo_exibidor
        schema:
          type: string
          example: 'CINEMARK'
        description: (Filtro Aninhado) Filtra por salas pertencentes a um grupo exibidor.
    responses:
      200:
        description: Uma lista paginada de salas com dados aninhados.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      registro_sala:
                        type: string
                        description: Identificador único da sala
                      nome_sala:
                        type: string
                        description: Nome oficial da sala
                      situacao_sala:
                        type: string
                        description: Situação operacional
                      tipo_tela:
                        type: string
                        description: Tecnologia de projeção
                      tipo_som:
                        type: string
                        description: Sistema de áudio
                      poltronas:
                        type: integer
                        description: Número de assentos
                      complexos:
                        type: object
                        properties:
                          registro_complexo:
                            type: string
                            description: Identificador único do complexo
                          nome_complexo:
                            type: string
                            description: Nome do complexo/shopping
                          uf_complexo:
                            type: string
                            description: Unidade federativa
                          municipio_complexo:
                            type: string
                            description: Município
                          endereco_complexo:
                            type: string
                            description: Endereço completo
                          exibidores:
                            type: object
                            properties:
                              registro_exibidor:
                                type: string
                                description: Identificador único do exibidor
                              nome_grupo_exibidor:
                                type: string
                                description: Nome do grupo empresarial
                              cnpj_exibidor:
                                type: string
                                description: CNPJ da empresa
                pagination:
                  type: object
                  properties:
                    total_filtered_count:
                      type: integer
                    per_page:
                      type: integer
                    next_cursor:
                      type: string
                    has_next:
                      type: boolean
      500:
        description: Erro interno do servidor.
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
    Busca detalhada de Obras Brasileiras
    ---
    tags:
      - Produção
    summary: Busca obras cinematográficas brasileiras com países de co-produção.
    description: >
      Retorna uma lista paginada de obras brasileiras com certificado CPB.
      Cada obra inclui um array `paises_origem` com todos os países envolvidos na produção,
      permitindo análises de co-produções internacionais e mapeamento da produção nacional.
    parameters:
      - in: query
        name: limit
        schema:
          type: integer
          default: 10
          maximum: 100
        description: Número de itens por página.
      - in: query
        name: last_id
        schema:
          type: string
        description: O cursor da página anterior (usar o `cpb`).
      - in: query
        name: tipo_obra
        schema:
          type: string
          enum: ['Longa-metragem', 'Curta-metragem', 'Documentário', 'Animação']
          example: 'Longa-metragem'
        description: Filtra por categoria da produção.
      - in: query
        name: genero
        schema:
          type: string
          example: 'Drama'
        description: Filtra por gênero cinematográfico.
      - in: query
        name: ano_producao
        schema:
          type: integer
          example: 2023
        description: Filtra por ano de finalização da produção.
      - in: query
        name: situacao
        schema:
          type: string
          enum: ['Finalizada', 'Em Produção', 'Pré-produção']
          example: 'Finalizada'
        description: Filtra por status atual da obra.
      - in: query
        name: paises_origem.pais
        schema:
          type: string
          example: 'França'
        description: (Filtro Aninhado) Filtra por obras com co-produção de um país específico.
    responses:
      200:
        description: Uma lista paginada de obras brasileiras com dados de co-produção.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      cpb:
                        type: string
                        description: Certificado de Produto Brasileiro
                      titulo_obra:
                        type: string
                        description: Título oficial da obra
                      tipo_obra:
                        type: string
                        description: Categoria da produção
                      genero:
                        type: string
                        description: Gênero cinematográfico
                      ano_producao:
                        type: integer
                        description: Ano de finalização
                      situacao:
                        type: string
                        description: Status atual
                      duracao_minutos:
                        type: integer
                        description: Duração em minutos
                      sinopse:
                        type: string
                        description: Resumo da obra
                      paises_origem:
                        type: array
                        items:
                          type: object
                          properties:
                            id:
                              type: integer
                              description: Identificador da relação
                            pais:
                              type: string
                              description: Nome do país
                            tipo_participacao:
                              type: string
                              description: Tipo de envolvimento
                pagination:
                  type: object
                  properties:
                    total_filtered_count:
                      type: integer
                    per_page:
                      type: integer
                    next_cursor:
                      type: string
                    has_next:
                      type: boolean
      500:
        description: Erro interno do servidor.
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
    Distribuição de Salas por Estado
    ---
    tags:
      - KPIs
    summary: Estatísticas de infraestrutura de exibição por UF.
    description: >
      Retorna dados agregados da distribuição de salas de cinema por unidade federativa.
      Inclui contagem total de salas, poltronas e complexos por estado, permitindo
      análises de concentração geográfica da infraestrutura cinematográfica brasileira.
    responses:
      200:
        description: Estatísticas de salas agrupadas por UF.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  uf_complexo:
                    type: string
                    description: Unidade federativa
                    example: 'SP'
                  total_salas:
                    type: integer
                    description: Número total de salas no estado
                    example: 1250
                  total_poltronas:
                    type: integer
                    description: Capacidade total de assentos
                    example: 180000
                  media_poltronas_por_sala:
                    type: number
                    format: float
                    description: Média de poltronas por sala
                    example: 144.5
                  total_complexos:
                    type: integer
                    description: Número de complexos cinematográficos
                    example: 85
      500:
        description: Erro interno do servidor.
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
    Distribuição de Obras por Categoria
    ---
    tags:
      - KPIs
    summary: Estatísticas da produção brasileira por tipo de obra.
    description: >
      Retorna dados agregados da produção cinematográfica brasileira agrupados por categoria.
      Inclui contagem total e duração média por tipo (longa-metragem, curta-metragem, etc.),
      permitindo análises do perfil da produção nacional.
    responses:
      200:
        description: Estatísticas de obras agrupadas por tipo.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  tipo_obra:
                    type: string
                    description: Categoria da produção
                    example: 'Longa-metragem'
                  total_obras:
                    type: integer
                    description: Número total de obras do tipo
                    example: 450
                  duracao_media:
                    type: number
                    format: float
                    description: Duração média em minutos
                    example: 105.5
      500:
        description: Erro interno do servidor.
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
    """
    Market Share do Cinema Nacional
    ---
    tags:
      - KPIs
    summary: Participação do cinema brasileiro no mercado nacional.
    description: >
      Calcula o percentual de público e renda do cinema nacional versus estrangeiro.
      Agrupa lançamentos por origem (CPB para brasileiros, ROE para estrangeiros) e
      retorna métricas comparativas essenciais para análise de mercado.
    responses:
      200:
        description: Dados de market share nacional vs estrangeiro.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  tipo:
                    type: string
                    enum: ['Nacional', 'Estrangeiro']
                    description: Origem da produção
                    example: 'Nacional'
                  publico_total:
                    type: integer
                    description: Número total de espectadores
                    example: 15000000
                  renda_total:
                    type: number
                    format: decimal
                    description: Receita total em reais
                    example: 180000000.00
                  percentual_publico:
                    type: number
                    format: float
                    description: Percentual do público total
                    example: 12.50
                  percentual_renda:
                    type: number
                    format: float
                    description: Percentual da renda total
                    example: 8.75
      500:
        description: Erro interno do servidor.
    """
    try:
        response = supabase.rpc('calcular_market_share_nacional').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@data_bp.route('/estatisticas/ranking_distribuidoras', methods=['GET'])
def get_stats_ranking_distribuidoras():
    """
    Ranking de Distribuidoras por Bilheteria
    ---
    tags:
      - KPIs
    summary: Distribuidoras com maior desempenho comercial.
    description: >
      Lista as distribuidoras ordenadas por receita total, incluindo métricas de
      público, número de lançamentos e público médio por filme. Essencial para
      análises de concentração de mercado e performance das distribuidoras.
    responses:
      200:
        description: Ranking de distribuidoras por performance comercial.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  razao_social_distribuidora:
                    type: string
                    description: Nome da empresa distribuidora
                    example: 'DISNEY'
                  publico_total:
                    type: integer
                    description: Público total acumulado
                    example: 45000000
                  renda_total:
                    type: number
                    format: decimal
                    description: Receita total em reais
                    example: 850000000.00
                  total_lancamentos:
                    type: integer
                    description: Número de filmes lançados
                    example: 12
                  publico_medio_por_filme:
                    type: integer
                    description: Público médio por lançamento
                    example: 3750000
      500:
        description: Erro interno do servidor.
    """
    try:
        response = supabase.rpc('ranking_distribuidoras').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
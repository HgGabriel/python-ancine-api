# app/api/v1/__init__.py

# 1. Importar as *variáveis* de blueprint de cada ficheiro de endpoint

# Do seu ficheiro 'data.py' (salas, complexos, estatísticas de salas)
try:
    from .data import data_bp
except ImportError:
    print("Aviso: Blueprint 'data_bp' não encontrado.")
    data_bp = None

# Das novas fontes de dados
try:
    from .endpoints_obras import obras_bp
except ImportError:
    print("Aviso: Blueprint 'obras_bp' não encontrado.")
    obras_bp = None

try:
    from .endpoints_lancamentos import lancamentos_bp
except ImportError:
    print("Aviso: Blueprint 'lancamentos_bp' não encontrado.")
    lancamentos_bp = None

try:
    from .endpoints_producao import producao_bp
except ImportError:
    print("Aviso: Blueprint 'producao_bp' (filmagem) não encontrado.")
    producao_bp = None


# 2. Definir a função que o seu app/__init__.py chama
def register_blueprints(app):
    """
    Registra todos os blueprints da v1 com seus prefixos de URL.
    """
    
    # O 'data_bp' contém as rotas /data/..., /pesquisa-salas, /estatisticas/salas_por_uf
    # Vamos registá-lo na raiz da v1
    if data_bp:
        app.register_blueprint(data_bp, url_prefix='/api/v1')
        
    # Os outros blueprints terão os seus próprios prefixos
    if obras_bp:
        app.register_blueprint(obras_bp, url_prefix='/api/v1/obras')
        
    if lancamentos_bp:
        app.register_blueprint(lancamentos_bp, url_prefix='/api/v1/lancamentos')
        
    if producao_bp:
        app.register_blueprint(producao_bp, url_prefix='/api/v1/producao')
        
    print("Blueprints da V1 registados com sucesso.")
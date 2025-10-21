# app/models/db_models.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# --- Domínio: Exibição (salas-de-exibicao-e-complexos.csv) ---

class ExibidorDBModel(BaseModel):
    registro_exibidor: str
    cnpj_exibidor: str
    nome_exibidor: str
    nome_grupo_exibidor: Optional[str] = None
    situacao_exibidor: Optional[str] = None

class ComplexoDBModel(BaseModel):
    registro_complexo: str
    registro_exibidor_fk: str
    situacao_complexo: Optional[str] = None
    data_situacao_complexo: Optional[date] = None
    website_complexo: Optional[str] = None
    complexo_itinerante: bool
    tipo_operacao_usual: Optional[str] = None
    endereco_complexo: Optional[str] = None
    numero_endereco_complexo: Optional[str] = None
    complemento_complexo: Optional[str] = None
    bairro_complexo: Optional[str] = None
    municipio_complexo: Optional[str] = None
    uf_complexo: Optional[str] = None
    cep_complexo: Optional[str] = None

class SalaDBModel(BaseModel):
    registro_sala: str
    registro_complexo_fk: str
    nome_sala: str
    cnpj_sala: Optional[str] = None
    situacao_sala: Optional[str] = None
    data_situacao_sala: Optional[date] = None
    data_inicio_funcionamento: Optional[date] = None
    assentos_total: Optional[int] = None
    assentos_cadeirantes: Optional[int] = None
    assentos_mobilidade_reduzida: Optional[int] = None
    assentos_obesidade: Optional[int] = None
    acesso_assentos_rampa: bool
    acesso_sala_rampa: bool
    banheiros_acessiveis: bool

# --- Domínio: Obras (obras-nao-pub...csv) ---

class ObraDBModel(BaseModel):
    cpb: str
    titulo_original: Optional[str] = None
    data_emissao_cpb: Optional[date] = None
    situacao_obra: Optional[str] = None
    tipo_obra: Optional[str] = None
    subtipo_obra: Optional[str] = None
    classificacao_obra: Optional[str] = None
    organizacao_temporal: Optional[str] = None
    duracao_total_minutos: Optional[float] = None
    quantidade_episodios: Optional[int] = None
    ano_producao_inicial: Optional[int] = None
    ano_producao_final: Optional[int] = None
    segmento_destinacao_inicial: Optional[str] = None # <-- Coluna corrigida
    coproducao_internacional: bool
    requerente: Optional[str] = None
    cnpj_requerente: Optional[str] = None
    uf_requerente: Optional[str] = None
    municipio_requerente: Optional[str] = None

# --- Domínio: Países (paises-de-origem...csv) ---
# (Este é o modelo da sua tabela relacional 'paises_origem')
class PaisOrigemDBModel(BaseModel):
    id: int # Chave primária SERIAL
    obra_cpb_fk: str
    pais_origem: str
    titulo_original_pais: Optional[str] = None
    
# --- Domínio: Distribuição (lancamentos-comerciais...csv) ---

class DistribuidoraDBModel(BaseModel):
    """Representação 1:1 da tabela 'distribuidoras'"""
    registro_distribuidora: int
    cnpj_distribuidora: Optional[str] = None
    razao_social_distribuidora: Optional[str] = None

class LancamentoDBModel(BaseModel):
    """Representação 1:1 da tabela 'lancamentos'"""
    id: int # Chave primária SERIAL
    obra_cpb_fk: Optional[str] = None # Pode ser nulo (filmes estrangeiros)
    registro_distribuidora_fk: Optional[int] = None
    cpb_roe: str
    titulo_original: Optional[str] = None
    data_lancamento: Optional[date] = None
    tipo_obra: Optional[str] = None
    pais_obra: Optional[str] = None
    publico_total: Optional[int] = None
    renda_total: Optional[Decimal] = None # Usar Decimal para valores monetários    
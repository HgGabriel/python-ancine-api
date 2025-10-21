# app/models/api_models.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal

# --- Modelos para o endpoint /pesquisa-salas ---
# (Correspondem à estrutura do seu endpoint com JOINs)

class ExibidorNestedModel(BaseModel):
    """Modelo simplificado de Exibidor para aninhamento"""
    nome_exibidor: Optional[str] = None
    nome_grupo_exibidor: Optional[str] = None

class ComplexoNestedModel(BaseModel):
    """Modelo simplificado de Complexo (como no seu exemplo)"""
    registro_complexo: str
    municipio_complexo: Optional[str] = None
    uf_complexo: Optional[str] = None
    # Aninha o exibidor dentro do complexo
    exibidores: ExibidorNestedModel

class SalaAPIResponse(BaseModel):
    """Modelo de resposta principal para /pesquisa-salas"""
    registro_sala: str
    nome_sala: Optional[str] = None
    situacao_sala: Optional[str] = None
    assentos_total: Optional[int] = None
    # Aninha o complexo (que contém o exibidor) dentro da sala
    complexos: ComplexoNestedModel


# --- Modelos para um endpoint de /pesquisa-obras ---
# (Baseado no seu 'ObraBrasileiraModel', mas corrigido)

class PaisOrigemNestedModel(BaseModel):
    """
    Modelo para a lista de países de uma obra.
    Baseado na tabela 'paises_origem'.
    """
    pais_origem: str

class ObraAPIResponse(BaseModel):
    """
    Modelo de resposta principal para /pesquisa-obras.
    Ele usa 'alias' para corresponder aos nomes que você queria.
    """
    cpb: str = Field(alias="registro_obra")
    titulo_original: Optional[str] = Field(alias="titulo_obra")
    ano_producao_inicial: Optional[int] = Field(alias="ano_producao")
    tipo_obra: Optional[str] = Field(alias="genero")
    duracao_total_minutos: Optional[float] = Field(alias="duracao_minutos")
    
    # Uma obra pode ter MÚLTIPLOS países de origem,
    # então o correto é ter uma LISTA.
    paises_origem: List[PaisOrigemNestedModel] = []
    
    class Config:
        populate_by_name = True # Permite usar 'registro_obra' ou 'cpb'
        
class DistribuidoraNestedModel(BaseModel):
    """Modelo simplificado de Distribuidora para aninhamento"""
    registro_distribuidora: int
    razao_social_distribuidora: Optional[str] = None
    cnpj_distribuidora: Optional[str] = None


class LancamentoAPIResponse(BaseModel):
    """
    Modelo de resposta principal para o endpoint /lancamentos/pesquisa
    """
    id: int
    cpb_roe: str
    titulo_original: Optional[str] = None
    data_lancamento: Optional[date] = None
    tipo_obra: Optional[str] = None
    pais_obra: Optional[str] = None
    publico_total: Optional[int] = None
    renda_total: Optional[Decimal] = None
    
    # --- Dados Aninhados (JOINs) ---
    
    # O seu select 'distribuidoras!inner(*)' garante que
    # 'distribuidoras' nunca será nulo.
    distribuidoras: DistribuidoraNestedModel
    
    # O seu select 'obras(*)' permite que 'obras' seja nulo
    # (o que acontece em filmes estrangeiros com CPB 'E...').
    obras: Optional[ObraAPIResponse] = None # Pode reutilizar o ObraAPIResponse        
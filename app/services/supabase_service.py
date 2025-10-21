# app/services/supabase_service.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv() 

supabase = None
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    print("Erro Fatal: A variável SUPABASE_URL não foi encontrada.")
    print("Verifique se o seu arquivo .env está na pasta raiz e contém SUPABASE_URL.")
elif not key:
    print("Erro Fatal: A variável SUPABASE_KEY não foi encontrada.")
    print("Verifique se o seu arquivo .env está na pasta raiz e contém SUPABASE_KEY.")
else:
    try:
        # Tenta criar a instância do cliente Supabase
        supabase: Client = create_client(url, key)
        print("Cliente Supabase inicializado com sucesso!") # Adicionamos um sucesso
        
    except Exception as e:
        print(f"Erro ao inicializar o cliente Supabase (mesmo com as chaves): {e}")
        supabase = None
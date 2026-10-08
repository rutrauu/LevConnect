"""
LevConnect - Runner Script
Executa o servidor local do LevConnect na porta 8000.
"""

import sys
import os
import webbrowser
import uvicorn

# Adiciona o diretório backend ao sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

if __name__ == "__main__":
    print("=" * 60)
    print("  LevConnect - CRM e Vendas Omnichannel (Lojas Lev)")
    print("  Iniciando servidor local em http://127.0.0.1:8000")
    print("=" * 60)
    
    # Inicia o uvicorn com reload ativo para desenvolvimento
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

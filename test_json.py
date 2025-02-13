import json
import os
from datetime import datetime

# Teste de escrita
def test_json_write():
    data = [{
        'cliente': 'TESTE',
        'etapa': 'TESTE',
        'status': 'Em andamento',
        'data_modificacao': datetime.now().isoformat()
    }]
    
    try:
        with open('status_history.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, default=str, indent=2)
        print("Arquivo criado com sucesso!")
        
        # Teste de leitura
        with open('status_history.json', 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print("Dados lidos com sucesso:", loaded_data)
        
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    test_json_write() 
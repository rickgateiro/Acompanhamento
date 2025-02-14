from supabase import create_client, Client
from datetime import datetime
import os
from dotenv import load_dotenv

class SupabaseManager:
    def __init__(self):
        # Carrega variáveis de ambiente do arquivo .env
        load_dotenv()
        
        # Inicializa o cliente Supabase com as credenciais diretamente
        self.supabase = create_client(
            "https://fwiilsnqazddwookkrdd.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ3aWlsc25xYXpkZHdvb2trcmRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk0NzcxNTEsImV4cCI6MjA1NTA1MzE1MX0.P8WS526WRNR_H8NWILDalt88xYzB9G0MhmZOAB48lVo"
        )

    def get_current_status(self, cliente, etapa):
        try:
            result = self.supabase.table('status_history').select('*')\
                .eq('cliente', cliente)\
                .eq('etapa', etapa)\
                .order('data_modificacao', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['status']
            return 'Não iniciada'
        except Exception as e:
            print(f"Erro ao buscar status: {str(e)}")
            return 'Não iniciada'

    def save_status_changes(self, status_updates):
        try:
            print("Iniciando salvamento de atualizações...")
            print(f"Dados recebidos: {status_updates}")
            
            data = []
            for update in status_updates:
                data.append({
                    'cliente': update['cliente'],
                    'etapa': update['etapa'],
                    'status': update['status'],
                    'data_modificacao': datetime.now().isoformat()
                })
            
            print(f"Dados formatados para inserção: {data}")
            result = self.supabase.table('status_history').insert(data).execute()
            print(f"Resposta do Supabase: {result.data}")
            return True
        except Exception as e:
            print(f"Erro ao salvar registros: {str(e)}")
            print(f"Tipo do erro: {type(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return False 
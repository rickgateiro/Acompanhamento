from supabase import create_client, Client
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicialização do Supabase
supabase: Client = create_client(
    os.environ.get("https://fwiilsnqazddwookkrdd.supabase.co"),
    os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ3aWlsc25xYXpkZHdva2tycmRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk0NzcxNTEsImV4cCI6MjA1NTA1MzE1MX0.P8WS526WRNR_H8NWILDalt88xYzB9G0MhmZOAB48lVo")
)

def generate_weekly_report(start_date=None, end_date=None):
    """
    Gera um relatório semanal das mudanças de status
    """
    if not start_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
    
    try:
        # Buscar dados do período
        result = supabase.table('status_history')\
            .select('*')\
            .gte('data_modificacao', start_date.isoformat())\
            .lte('data_modificacao', end_date.isoformat())\
            .execute()
        
        # Converter para DataFrame
        df = pd.DataFrame(result.data)
        
        if df.empty:
            return pd.DataFrame(columns=['cliente', 'etapa', 'status', 'data_modificacao'])
        
        # Criar relatório resumido
        report = df.groupby(['cliente', 'etapa']).agg({
            'status': 'last',
            'data_modificacao': 'last'
        }).reset_index()
        
        return report
    
    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")
        return pd.DataFrame()

def generate_detailed_report(start_date=None, end_date=None):
    """
    Gera um relatório detalhado com todas as mudanças de status no período
    """
    if not start_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
    
    try:
        result = supabase.table('status_history')\
            .select('*')\
            .gte('data_modificacao', start_date.isoformat())\
            .lte('data_modificacao', end_date.isoformat())\
            .order('data_modificacao', desc=True)\
            .execute()
        
        return pd.DataFrame(result.data)
    
    except Exception as e:
        print(f"Erro ao gerar relatório detalhado: {str(e)}")
        return pd.DataFrame()

if __name__ == '__main__':
    # Gerar relatório resumido
    report = generate_weekly_report()
    print("\nRelatório Resumido:")
    print(report)
    
    # Salvar em Excel
    filename = f'relatorio_keepdoc_{datetime.now().strftime("%Y%m%d")}'
    report.to_excel(f'{filename}_resumido.xlsx', index=False)
    
    # Gerar relatório detalhado
    detailed_report = generate_detailed_report()
    print("\nRelatório Detalhado:")
    print(detailed_report)
    detailed_report.to_excel(f'{filename}_detalhado.xlsx', index=False)
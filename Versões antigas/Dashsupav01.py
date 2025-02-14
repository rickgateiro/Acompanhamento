import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
from datetime import datetime
from supabase import create_client, Client

# Inicialização do Supabase com suas credenciais
supabase = create_client(
    "https://fwiilsnqazddwookkrdd.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ3aWlsc25xYXpkZHdvb2trcmRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk0NzcxNTEsImV4cCI6MjA1NTA1MzE1MX0.P8WS526WRNR_H8NWILDalt88xYzB9G0MhmZOAB48lVo"
)

# Inicialização do app Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Dados iniciais
clientes = ['RIOPREVIDENCIA', 'UENF', 'PRODERJ']
etapas = ['Instalação e Configuração do RDC', 'Cadastro e Permissionamento dos Usuários', 
          'Go-Live (Entrada em Produção)', 'Suporte Pós-Implantação']
# Status options with their respective colors
status_options = [
    {'label': 'Não iniciada', 'value': 'Não iniciada', 'color': '#dc3545'},  # Red
    {'label': 'Em andamento', 'value': 'Em andamento', 'color': '#ffa500'},  # Orange
    {'label': 'Concluída', 'value': 'Concluída', 'color': '#28a745'}        # Green
]

# Função para normalizar IDs
def normalize_id(text):
    """Normaliza o texto para usar como ID removendo acentos e caracteres especiais"""
    import unicodedata
    normalized = unicodedata.normalize('NFKD', text)
    normalized = normalized.encode('ASCII', 'ignore').decode('ASCII')
    normalized = normalized.replace(' ', '-').replace('(', '').replace(')', '')
    return normalized

# Função para obter o status atual do Supabase
def get_current_status(cliente, etapa):
    try:
        result = supabase.table('status_history').select('*')\
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

# Layout do app
app.layout = html.Div([
    html.H1('ACOMPANHAMENTO DE IMPLANTAÇÃO DO KEEPDOC', 
            style={'textAlign': 'center', 
                   'backgroundColor': '#007bff',
                   'color': 'white', 
                   'padding': '20px',
                   'fontFamily': 'Arial, sans-serif'}),
    
    html.Div(id='clientes-progresso'),
    
    dcc.Interval(
        id='interval-component',
        interval=60*1000,
        n_intervals=0
    ),
    html.Div(id='status-store', style={'display': 'none'})
], style={'backgroundColor': '#d4edda', 'minHeight': '100vh'})

def gerar_progresso_implementacao():
    progresso = []
    for cliente in clientes:
        cliente_container = html.Div([
            html.H3(cliente, 
                   style={'textAlign': 'center', 
                         'backgroundColor': '#007bff', 
                         'color': 'white', 
                         'padding': '10px',
                         'fontFamily': 'Arial, sans-serif'}),
            html.Div([
                html.Div([
                    html.Div(etapa, style={'fontWeight': 'bold', 
                                         'marginBottom': '10px',
                                         'fontFamily': 'Arial, sans-serif'}),
                    dcc.Dropdown(
                        id=f'status-{normalize_id(cliente)}-{normalize_id(etapa)}',
                        options=[{
                            'label': html.Div([
                                html.Span('●', style={
                                    'color': status['color'],
                                    'marginRight': '10px',
                                    'fontSize': '20px'
                                }),
                                status['label']
                            ], style={'display': 'flex', 'alignItems': 'center'}),
                            'value': status['value']
                        } for status in status_options],
                        value=get_current_status(cliente, etapa),
                        clearable=False
                    )
                ], style={'padding': '10px', 
                         'margin': '5px', 
                         'border': '1px solid #ccc', 
                         'borderRadius': '5px',
                         'backgroundColor': 'white',
                         'fontFamily': 'Arial, sans-serif'})
                for etapa in etapas
            ], style={'display': 'flex', 
                     'justifyContent': 'center',
                     'backgroundColor': '#f8f9fa', 
                     'padding': '20px'})
        ], style={'margin': '20px auto', 
                  'border': '1px solid #ddd', 
                  'borderRadius': '5px',
                  'maxWidth': '1200px',
                  'backgroundColor': 'white'})
        
        progresso.append(cliente_container)
    return progresso

@app.callback(
    Output('clientes-progresso', 'children'),
    [Input('status-store', 'children'),
     Input('interval-component', 'n_intervals')]
)
def atualizar_progresso(status_changed, n_intervals):
    return gerar_progresso_implementacao()

@app.callback(
    Output('status-store', 'children'),
    [Input(f'status-{normalize_id(cliente)}-{normalize_id(etapa)}', 'value')
     for cliente in clientes
     for etapa in etapas],
    [State(f'status-{normalize_id(cliente)}-{normalize_id(etapa)}', 'id')
     for cliente in clientes
     for etapa in etapas]
)
def save_status_changes(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    print("Callback acionado!")
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    new_value = ctx.triggered[0]['value']
    
    # Extrair cliente e etapa do ID do componente
    _, cliente_norm, *etapa_parts = trigger_id.split('-')
    
    # Encontrar o cliente e etapa originais
    cliente = next(c for c in clientes if normalize_id(c) == cliente_norm)
    etapa = next(e for e in etapas if normalize_id(e) in '-'.join(etapa_parts))
    
    try:
        # Inserir novo registro no Supabase
        data = {
            'cliente': cliente,
            'etapa': etapa,
            'status': new_value,
            'data_modificacao': datetime.now().isoformat()
        }
        
        result = supabase.table('status_history').insert(data).execute()
        print(f"Registro salvo com sucesso: {result.data}")
        
        return "Atualizado"
    except Exception as e:
        print(f"Erro ao salvar registro: {str(e)}")
        return "Erro"

if __name__ == '__main__':
    app.run_server(debug=True)
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
from datetime import datetime
import json
import os

# Inicialização do app Dash com suppress_callback_exceptions=True
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

# Função para carregar dados do arquivo JSON
def load_status_history():
    if os.path.exists('status_history.json'):
        try:
            with open('status_history.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

# Função para salvar dados no arquivo JSON
def save_status_history(data):
    try:
        with open('status_history.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, default=str, indent=2)
        print(f"Arquivo JSON salvo com sucesso! Total de registros: {len(data)}")
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON: {str(e)}")

# Função para obter o status atual
def get_current_status(cliente, etapa):
    history = load_status_history()
    # Filtra registros para o cliente e etapa específicos
    registros = [r for r in history if r['cliente'] == cliente and r['etapa'] == etapa]
    if registros:
        # Retorna o status mais recente
        return sorted(registros, key=lambda x: x['data_modificacao'])[-1]['status']
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
    html.Div(id='status-store', style={'display': 'none'})  # Div oculto para armazenar callbacks
], style={'backgroundColor': '#d4edda', 'minHeight': '100vh'})

# Modifique a função que normaliza os IDs
def normalize_id(text):
    """Normaliza o texto para usar como ID removendo acentos e caracteres especiais"""
    import unicodedata
    # Normaliza os caracteres Unicode
    normalized = unicodedata.normalize('NFKD', text)
    # Remove os acentos
    normalized = normalized.encode('ASCII', 'ignore').decode('ASCII')
    # Substitui espaços e outros caracteres por hífen
    normalized = normalized.replace(' ', '-').replace('(', '').replace(')', '')
    return normalized

# Modifique a função gerar_progresso_implementacao
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

# Modifique o callback para usar os IDs normalizados
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
    
    print("Callback acionado!")  # Log para debug
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    new_value = ctx.triggered[0]['value']
    
    print(f"Mudança detectada - ID: {trigger_id}, Novo valor: {new_value}")  # Log para debug
    
    # Extrair cliente e etapa do ID do componente usando os IDs normalizados
    _, cliente_norm, *etapa_parts = trigger_id.split('-')
    
    # Encontrar o cliente e etapa originais
    cliente = next(c for c in clientes if normalize_id(c) == cliente_norm)
    etapa = next(e for e in etapas if normalize_id(e) in '-'.join(etapa_parts))
    
    print(f"Cliente: {cliente}, Etapa: {etapa}")  # Log para debug
    
    # Carregar histórico existente
    history = load_status_history()
    print(f"Histórico atual carregado: {len(history)} registros")  # Log para debug
    
    # Adicionar novo registro
    novo_registro = {
        'cliente': cliente,
        'etapa': etapa,
        'status': new_value,
        'data_modificacao': datetime.now().isoformat()
    }
    history.append(novo_registro)
    
    print(f"Novo registro adicionado: {novo_registro}")  # Log para debug
    
    # Salvar histórico atualizado
    save_status_history(history)
    return "Atualizado"

if __name__ == '__main__':
    # Criar arquivo JSON vazio se não existir
    if not os.path.exists('status_history.json'):
        save_status_history([])
        print("Arquivo JSON inicial criado")
    
    print("Diretório atual:", os.getcwd())
    app.run_server(debug=True)
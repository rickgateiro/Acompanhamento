"""
KEEPDOC - Sistema de Acompanhamento de Implantação
Versão: 1.0.0
Data: 2024-03-19
Autor: Rick
Descrição: Frontend do sistema de acompanhamento de implantação do KEEPDOC.
           Permite o monitoramento e atualização do status de diferentes etapas
           do processo de implantação para múltiplos clientes.

Histórico de Versões:
- 1.0.0 (2024-03-19):
  * Versão inicial
  * Interface com dropdowns para atualização de status
  * Integração com Supabase para persistência dos dados
  * Sistema de salvamento manual de alterações
  * Feedback visual do status com cores
  * Suporte a múltiplos clientes e etapas
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL
from backend import SupabaseManager
import json

# Inicialização
app = dash.Dash(__name__, suppress_callback_exceptions=True)
supabase_manager = SupabaseManager()

# Dados iniciais
clientes = ['RIOPREVIDENCIA', 'UENF', 'PRODERJ']
etapas = ['Instalação e Configuração do RDC', 'Cadastro e Permissionamento dos Usuários', 
          'Go-Live (Entrada em Produção)', 'Suporte Pós-Implantação']
status_options = [
    {'label': 'Não iniciada', 'value': 'Não iniciada', 'color': '#dc3545'},
    {'label': 'Em andamento', 'value': 'Em andamento', 'color': '#ffa500'},
    {'label': 'Concluída', 'value': 'Concluída', 'color': '#28a745'}
]

def normalize_id(text):
    import unicodedata
    normalized = unicodedata.normalize('NFKD', text)
    normalized = normalized.encode('ASCII', 'ignore').decode('ASCII')
    normalized = normalized.replace(' ', '-').replace('(', '').replace(')', '')
    return normalized

# Layout do app
app.layout = html.Div([
    html.H1('ACOMPANHAMENTO DE IMPLANTAÇÃO DO KEEPDOC', 
            style={'textAlign': 'center', 
                   'backgroundColor': '#007bff',
                   'color': 'white', 
                   'padding': '20px',
                   'fontFamily': 'Arial, sans-serif'}),
    
    html.Div(id='clientes-progresso'),
    
    html.Button('Salvar Alterações', 
                id='btn-salvar',
                style={
                    'margin': '20px',
                    'padding': '10px 20px',
                    'backgroundColor': '#28a745',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }),
    
    html.Div(id='mensagem-salvamento', 
             style={'textAlign': 'center', 'margin': '10px'}),
    
    dcc.Store(id='status-changes', data=[]),
    
    # Comentando o componente de intervalo
    # dcc.Interval(
    #     id='interval-component',
    #     interval=60*1000,
    #     n_intervals=0
    # )
], style={'backgroundColor': '#d4edda', 'minHeight': '100vh'})

def gerar_progresso_implementacao(status_changes=None):
    progresso = []
    stored_changes = status_changes or []
    
    # Debug
    print("Status changes recebidos:", stored_changes)
    
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
                        id={'type': 'status-dropdown',
                            'cliente': cliente,
                            'etapa': etapa},
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
                        value=next(
                            (change['status'] 
                             for change in stored_changes 
                             if change['cliente'] == cliente and change['etapa'] == etapa),
                            supabase_manager.get_current_status(cliente, etapa)
                        ),
                        clearable=False,
                        persistence=True,  # Adiciona persistência ao dropdown
                        persistence_type='session'  # Mantém o valor durante a sessão
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
    [Output('status-changes', 'data'),
     Output('mensagem-salvamento', 'children')],
    [Input({'type': 'status-dropdown', 'cliente': ALL, 'etapa': ALL}, 'value'),
     Input('btn-salvar', 'n_clicks')],
    [State({'type': 'status-dropdown', 'cliente': ALL, 'etapa': ALL}, 'id'),
     State('status-changes', 'data')]
)
def handle_all_changes(values, n_clicks, ids, current_changes):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_changes or [], ""
    
    trigger = ctx.triggered[0]['prop_id']
    
    # Se o gatilho foi o botão de salvar
    if trigger == 'btn-salvar.n_clicks':
        if n_clicks is None:  # Se o botão não foi clicado ainda
            return current_changes or [], ""
        
        if current_changes:
            print("Tentando salvar alterações:", current_changes)
            if supabase_manager.save_status_changes(current_changes):
                return [], "Alterações salvas com sucesso!"
            return current_changes, "Erro ao salvar alterações."
        return current_changes or [], "Nenhuma alteração para salvar."
    
    # Se o gatilho foi uma mudança nos dropdowns
    try:
        current_changes = current_changes or []
        
        # Atualiza o status de todos os dropdowns
        new_changes = []
        for value, id_dict in zip(values, ids):
            if value is not None:
                cliente = id_dict['cliente']
                etapa = id_dict['etapa']
                
                # Verifica se o status é diferente do que está no Supabase
                current_status = supabase_manager.get_current_status(cliente, etapa)
                if value != current_status:
                    update = {
                        'cliente': cliente,
                        'etapa': etapa,
                        'status': value
                    }
                    new_changes.append(update)
                    print(f"Mudança detectada para {cliente} - {etapa}: {value}")
        
        if new_changes:
            return new_changes, "Alterações pendentes para salvar"
        return [], ""
        
    except Exception as e:
        print(f"Erro ao processar mudanças: {str(e)}")
        return current_changes or [], f"Erro ao processar mudanças: {str(e)}"

@app.callback(
    Output('clientes-progresso', 'children'),
    [Input('status-changes', 'data')]
)
def atualizar_progresso(status_changed):
    return gerar_progresso_implementacao(status_changed)

if __name__ == '__main__':
    app.run_server(debug=True) 
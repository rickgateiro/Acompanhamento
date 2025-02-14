import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output

# Script funcionando de forma simples. 

# Inicialização do app Dash
app = dash.Dash(__name__)

# Dados iniciais
clientes = ['RIOPREVIDENCIA', 'UENF']
etapas = ['Instalação e Configuração do RDC', 'Cadastro e Permissionamento dos Usuários', 
          'Go-Live (Entrada em Produção)', 'Suporte Pós-Implantação']
status_options = ['Não iniciada', 'Em andamento', 'Concluída']

# Layout do app
app.layout = html.Div([
    html.H1('ACOMPANHAMENTO DE IMPLANTAÇÃO DO KEEPDOC', 
            style={'textAlign': 'center', 'backgroundColor': '#d4edda', 'padding': '20px'}),
    
    html.Div(id='clientes-progresso'),
    
    dcc.Interval(
        id='interval-component',
        interval=60*1000,
        n_intervals=0
    )
])

def gerar_progresso_implementacao():
    progresso = []
    for cliente in clientes:
        cliente_container = html.Div([
            html.H3(cliente, 
                   style={'textAlign': 'center', 
                         'backgroundColor': '#007bff', 
                         'color': 'white', 
                         'padding': '10px'}),
            html.Div([
                html.Div([
                    html.Div(etapa, style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.Dropdown(
                        id=f'status-{cliente}-{etapa}'.replace(' ', '-'),
                        options=[{'label': status, 'value': status} 
                                for status in status_options],
                        value='Não iniciada',
                        clearable=False
                    )
                ], style={'padding': '10px', 
                         'margin': '5px', 
                         'border': '1px solid #ccc', 
                         'borderRadius': '5px',
                         'backgroundColor': 'white'})
                for etapa in etapas
            ], style={'display': 'flex', 
                     'backgroundColor': '#f8f9fa', 
                     'padding': '20px'})
        ], style={'margin': '20px', 
                  'border': '1px solid #ddd', 
                  'borderRadius': '5px'})
        
        progresso.append(cliente_container)
    return progresso

@app.callback(
    Output('clientes-progresso', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def atualizar_progresso(n):
    return gerar_progresso_implementacao()

if __name__ == '__main__':
    app.run_server(debug=True)
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output

# Inicialização do app Dash
app = dash.Dash(__name__)

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
    )
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
                        id=f'status-{cliente}-{etapa}'.replace(' ', '-'),
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
                        value='Não iniciada',
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
    [Input('interval-component', 'n_intervals')]
)
def atualizar_progresso(n):
    return gerar_progresso_implementacao()

if __name__ == '__main__':
    app.run_server(debug=True)
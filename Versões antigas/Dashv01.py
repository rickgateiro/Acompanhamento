import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output

# Inicialização do app Dash
app = dash.Dash(__name__)

# Dados iniciais
clientes = ['RIOPREVIDENCIA', 'UENF']
etapas = ['Instalação e Configuração do RDC', 'Cadastro e Permissionamento dos Usuários', 'Go-Live (Entrada em Produção)', 'Suporte Pós-Implantação']

# Layout do app
app.layout = html.Div([
    html.H1('Dashboard de Acompanhamento de Implantação do RDC-Arq', style={'textAlign': 'center', 'marginBottom': 50}),

    html.H2('Clientes e Etapas de Implementação', style={'textAlign': 'center'}),
    html.Div(id='clientes-etapas', style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'}),

    html.H2('Progresso da Implementação', style={'textAlign': 'center', 'marginTop': 50}),
    html.Div(id='progresso-implementacao', style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'}),

    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Atualiza a cada minuto
        n_intervals=0
    )
])

# Callback para atualizar clientes e etapas
@app.callback(
    Output('clientes-etapas', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def atualizar_clientes_etapas(n):
    return gerar_tabela_clientes_etapas()

# Callback para atualizar progresso
@app.callback(
    Output('progresso-implementacao', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def atualizar_progresso(n):
    return gerar_progresso_implementacao()

# Função para gerar a tabela de clientes e etapas
def gerar_tabela_clientes_etapas():
    tabela = []
    for cliente in clientes:
        for etapa in etapas:
            tabela.append(html.Div(f'{cliente} - {etapa}', style={'padding': '5px', 'margin': '5px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '200px', 'textAlign': 'center'}))
    return tabela

# Função para gerar o progresso de implementação
def gerar_progresso_implementacao():
    progresso = []
    for cliente in clientes:
        for etapa in etapas:
            progresso.append(html.Div(f'{cliente} - {etapa}: Em Progresso', style={'padding': '5px', 'margin': '5px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'width': '300px', 'textAlign': 'center'}))
    return progresso

if __name__ == '__main__':
    app.run_server(debug=True)
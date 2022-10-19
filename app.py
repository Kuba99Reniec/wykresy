import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd

dane_cawi_capi = pd.read_csv("dane_do_dasha.txt")
options = []
for col in dane_cawi_capi.columns[:-1]:
    options.append({'label':'{}'.format(col, col), 'value':col})
value = 'Wielkość gospodarstwa domowego (6 kategorii)'
wartosci = pd.read_csv('6_opis_wartości_zmiennych_20220819_opinie_km.txt', sep="\t")
zmienne = pd.read_csv('5_opis_zmiennych_20220819_podwojny_konwerter_opinie.txt', sep="\t")
wartosci = wartosci.merge(zmienne, on = "Nazwa zmiennej")
zmienna = 'RS: Płeć'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.H3('Porównanie rozkładów zmiennych: CAWI vs CAWI + CAPI (IX 2021 - VIII 2022)'),
    html.Label("Wybierz zmienną:"),
    dcc.Dropdown(
            id = 'my_dropdown',
            options= options,
            value='Choose columns'
        ),
    html.Label(id='my_label'),
    dcc.Graph(
        id='graph',
        figure=go.Figure()
    )
])

@app.callback(
    Output('graph', 'figure'),
    Input('my_dropdown', 'value'),
    State('graph', 'figure'),
)
def update_figure(value, fig):
    zmienna = value
    df_pom = pd.DataFrame(dane_cawi_capi[dane_cawi_capi['badanie'] == 'cawi'][zmienna].value_counts())
    names_cawi_pom = df_pom.index.to_list()
    values_cawi = df_pom[zmienna].to_list()
    values_cawi_capi = []
    names_cawi = []
    for i in names_cawi_pom:
        values_cawi_capi.append(len(dane_cawi_capi[dane_cawi_capi[zmienna] == i]))
        if zmienna in wartosci['Etykieta zmiennej'].to_list():
            names_cawi.append(
                wartosci[(wartosci['Etykieta zmiennej'] == zmienna) & (wartosci['wartość'] == i)]['Etykieta'].to_list()[
                    0])
        else:
            names_cawi = names_cawi_pom
    fig = go.Figure()
    fig.add_trace(go.Funnelarea(
        name="CAWI",
        scalegroup="first",
        text=names_cawi,
        values=values_cawi,
        showlegend=False,
        marker={"colors": ["lawngreen", "darkorange", "red", "yellow", "blue", "peru", "darkviolet"]},
        title={"position": "top center", "text": "CAWI"},
    ))
    fig.add_trace(go.Funnelarea(
        name="CAWI + CAPI",
        scalegroup="third",
        text=names_cawi,
        values=values_cawi_capi,
        textinfo="percent",
        title={"position": "top center", "text": "CAWI+CAPI"},
        showlegend=False,
        domain={"x": [.75, 1]}
    ))
    fig.update_layout(
        autosize=False,
        width=1150,
        height=600)
    fig.update_traces(title_font_size=20)
    fig.update_traces(title_position='top center')
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=25),
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

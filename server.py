
# # https://habr.com/company/ua-hosting/blog/281519/
# https://habr.com/company/ua-hosting/blog/434342/ Курс MIT «Безопасность компьютерных систем». Лекция 22: «Информационная безопасность MIT», часть 1

# нстройка Apache и mod_wsgi
# https://flask-russian-docs.readthedocs.io/ru/latest/deploying/mod_wsgi.html

# установка Apache + Python без фреймворка
# https://www.8host.com/blog/ustanovka-svyazki-apachemysqlpython-bez-frejmvorka-na-server-ubuntu-14-04/

# Настройка mod_wsgi (Apache) для Flask
# https://flask-russian-docs.readthedocs.io/ru/latest/deploying/mod_wsgi.html

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from pandas_datareader import data as web
from datetime import datetime as dt

app = dash.Dash('Hello World')

app.layout = html.Div([
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
        ],
        value='COKE'
    ),
    dcc.Graph(id='my-graph')
], style={'width': '500'})

@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    df = web.DataReader(
        selected_dropdown_value,
        'google',
        dt(2017, 1, 1),
        dt.now()
    )
    return {
        'data': [{
            'x': df.index,
            'y': df.Close
        }],
        'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
    }

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

if __name__ == '__main__':
    app.run_server(debug=True)
    
# http://www.linux16.ru/articles/kak-v-linux-sdelat-probros-portov.html
# https://bogachev.biz/2016/01/13/probros-i-perenapravlenie-portov-v-iptables/

# https://sites.google.com/site/javatokens/sqlite
# https://habr.com/post/149635/
import jwt
import datetime
import time
from dash.exceptions import PreventUpdate
import dash
import dash_design_kit as ddk
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px



app = dash.Dash(__name__)
server = app.server  # expose server variable for Procfile

df = px.data.stocks()

def plotly_validate_jwt(get_function):
        """Plotly Route/Callback protector using JWT (JSON Web Token) validation. This validator 
        will ensure that the token is formed properly, is the same as the token that was provided
        to the user, and that it hasn't expired (exp). The intended usage of this function is as 
        a decorator for routes that should be behind an authentication wall. 
        
        The decorated function will only run if the provided token is still valid and it checks 
        against 'session_token' which should be scoped to a single user's session.

        kwargs:
        'user_token': ... || This is the token that is compared against the session token.

        Unlike the generic version, this validator will 

        A proper implementation of this would probably involve setting cookies in a user browser 
        and comparing against that, but for now a session-based authenticator should work.
        """
    def wrapper(*args, **kwargs):
        try:
            jwt.decode(kwargs['user_token'], key, algorithms="HS256")
            if kwargs['user_token'] == session_token :
                return get_function(*args, **kwargs)
            print('recieved invalid token')
            raise PreventUpdate
        except jwt.exceptions.ExpiredSignatureError:
            print('recieved expired token')
            raise PreventUpdate
        except jwt.exceptions.DecodeError:
            print('malformed token')
            raise PreventUpdate
    return wrapper



app.layout = ddk.App([
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('logo.png')),
        ddk.Title('Dash Enterprise Sample Application'),
    ]),
    ddk.Row(children=[
        ddk.Card(children=[
            ddk.CardHeader(children=[
                dcc.Dropdown(
                    id='title-dropdown',
                    options=[{'label': i, 'value': i}
                        for i in ['GOOG', 'AAPL', 'AMZN']],
                    value='GOOG'
                )
            ]),
            ddk.Graph(id='update-graph', style={'height':300}),
        ]),
    ]),

    ddk.Row(children=[
        ddk.Card(width=50, children=ddk.Graph(figure=px.line(df, x="date", y=["AMZN", "FB"], title='Stock Prices'))),

        ddk.Card(width=50, children=ddk.Graph(figure=px.line(df, x="date", y=["AAPL", "MSFT"], title='Stock Prices')))
    ])
])


@app.callback(Output('update-graph', 'figure'),
              [Input('title-dropdown', 'value')])
def update_graph(value):
    @plotly_validate_jwt
    def get_value(value, user_token):
        if value == 'GOOG':
            return px.line(df, x="date", y="GOOG", title='Google Stock Price')
        elif value == 'AAPL':
            return px.line(df, x="date", y="AAPL", title='Apple Stock Price')
        elif value == 'AMZN':
            return px.line(df, x="date", y="AMZN", title='Amazon Stock Price')
    return get_value(value, user_token=session_token)


 
def test():
    def _validate_jwt(get_function):
        """Generic route/function protector using JWT (JSON Web Token) validation. This validator 
        will ensure that the token is formed properly, is the same as the token that was provided
        to the user, and that it hasn't expired (exp). The intended usage of this function is as 
        a decorator for routes that should be behind an authentication wall. 
        
        The decorated function will only run if the provided token is still valid and it checks 
        against 'session_token' which should be scoped to a single user's session.

        kwargs:
        'user_token': ... || This is the token that is compared against the session token.

        A proper implementation of this would probably involve setting cookies in a user browser 
        and comparing against that, but for now a session-based authenticator should work.
        """
        def wrapper(*args, **kwargs):
            try:
                jwt.decode(kwargs['user_token'], key, algorithms="HS256")
                if kwargs['user_token'] == session_token :
                    return get_function(*args, **kwargs)
                return 'invalid'
            except jwt.exceptions.ExpiredSignatureError:
                return 'expired'
            except jwt.exceptions.DecodeError:
                return 'malformed'
        return wrapper

    key = 'secret'
    session_token = jwt.encode({"username":"Test", 'password':'my_pass','exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=2), 'iss':'Gov_Lambda'}, key, algorithm="HS256", headers={})
    
    @_validate_jwt
    def get_request(user_token):
        return 'valid'

    false_token = 'bad_actor'

    print(f'The token { session_token } is {get_request(user_token=session_token)}')
    print(f'The token {false_token} is {get_request(user_token=false_token)}')

    time.sleep(2)

    print(f'The token { session_token } is {get_request(user_token=session_token)}')   

if __name__ == '__main__':
    key = 'secret'
    session_token = jwt.encode({"username":"Test", 'password':'my_pass','exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=10), 'iss':'Gov_Lambda'}, key, algorithm="HS256", headers={})
    false_token = 'bad_actor.sdf.sdfsd'
    print(jwt.decode(session_token, key, algorithms="HS256"))
    print(jwt.get_unverified_header(session_token))    
    
    test()
    #app.run_server(debug=True)


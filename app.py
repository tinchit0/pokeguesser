import base64
from io import BytesIO

import numpy as np
import pandas as pd
from dash import Dash, html, Input, Output, dcc
from skimage.io import imread, imsave

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = pd.read_csv('data/pokemon.csv')
pokeball_path = "data/img/Pokeball.png"
app = Dash(external_stylesheets=external_stylesheets)
game = {}


def get_stats():
    data_shown = game["N"] * (256 + 256 * 4 + 1)
    return [
        html.P(f"Number of singular values: {game['N']}"),
        html.P(f"Data shown: {data_shown}B"),
        html.P(f"Compression: {(1-data_shown/(256**2*4))*100:.2f}%"),
    ]


def img2src(img):
    buffered = BytesIO()
    imsave(buffered, img, "pil")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"


def reduce_image():
    N = game["N"]
    U, s, VT = game["SVD"]
    sigma = np.diag(s)
    red = U[:, :N] @ sigma[:N, :N] @ VT[:N, :]
    red[red < 0] = 0
    red[red > 255] = 255
    red = red.astype("uint8")
    return red.reshape((256, 256, 4))


app.layout = [
    html.Div([
        html.Div([
            html.Button('New Game', id='start-button', n_clicks=0, style={"width": "100%"}),
            html.Img(id="image", width="300", src=img2src(imread(pokeball_path)), style={"padding": 50}),
            dcc.Dropdown(id="user-guess", options=df["name"], multi=False, placeholder='Search...'),
            html.Div("Press 'New Game' to get started", id="message", style={"fontWeight": "bold", "font-size": "large", "padding": 20}),
        ], id='container', style={"textAlign": "center"}, className="six columns"),
        html.Div("", id="stats", className="six columns", style={"padding": 50, "fontWeight": "bold"}),
    ], className="row")
]


@app.callback(
    [
        Output('image', 'src', allow_duplicate=True),
        Output('message', 'children', allow_duplicate=True),
        Output('stats', 'children', allow_duplicate=True),
    ],
    Input('start-button', 'n_clicks'),
    prevent_initial_call=True,
)
def start_game(n_clicks):
    if n_clicks > 0:
        pokemon = df.sample(1).iloc[0]['name']
        img = imread(f"data/img/{pokemon}.png")
        game["pokemon"] = pokemon
        game["solution_img"] = img
        game["N"] = 1
        game["SVD"] = np.linalg.svd(img.reshape((256 * 4, 256)))
        game["img"] = reduce_image()
        return img2src(game["img"]), "Go!", get_stats()
    else:
        return img2src(imread(pokeball_path)), "Press 'New Game' to get started", []


@app.callback(
    [
        Output('image', 'src', allow_duplicate=True),
        Output('message', 'children', allow_duplicate=True),
        Output('stats', 'children', allow_duplicate=True),
    ],
    Input('user-guess', 'value'),
    prevent_initial_call=True,
)
def validate_guess(guess):
    if guess == game["pokemon"]:
        score = max(0, 11 - game["N"])
        return img2src(game["solution_img"]), f"You did it!! Your score: {score}", get_stats()
    else:
        game["N"] += 1
        game["img"] = reduce_image()
        return img2src(game["img"]), "Nope. Try again", get_stats()


if __name__ == '__main__':
    app.run(debug=True)

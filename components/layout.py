from dash import dcc, html

def create_layout():
    return html.Div([
        html.H1("Dashboard Interactif", style={'textAlign': 'center'}),

        # Composant d'upload
        html.Div([
            html.Label("Uploader un fichier CSV :"),
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Glissez un fichier ici ou ', html.A('cliquez pour sélectionner')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
        ]),

        # Dropdown pour choisir une colonne
        html.Div(id='dropdown-container', children=[
            html.Label("Choisissez une colonne :"),
            dcc.Dropdown(id='dropdown'),
        ], style={'width': '50%', 'margin': 'auto', 'display': 'none'}),  # Cacher le dropdown tant qu'il n'y a pas de fichier

        html.Div(id='stats', style={'margin-top': '20px'}),
        
        # Graphique interactif
        dcc.Graph(id='graph'),
        dcc.Graph(id='graph_pie'),
    ])

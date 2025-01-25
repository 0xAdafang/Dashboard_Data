from dash.dependencies import Input, Output, State
from dash import dcc, html
import plotly.express as px
import pandas as pd
import io
import base64

# Variable globale pour stocker les données chargées
dataframe_cache = pd.DataFrame()

def register_callbacks(app):
    @app.callback(
        [Output('dropdown', 'options'),
         Output('dropdown', 'value'),
         Output('dropdown-container', 'style')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def update_dropdown(file_content, filename):
        global dataframe_cache  # Utilisation de la variable globale
        if file_content is None:
            return [], None, {'display': 'none'}
        
        # Décoder le contenu du fichier
        content_type, content_string = file_content.split(',')
        decoded = base64.b64decode(content_string)
        dataframe_cache = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Générer les options pour le dropdown
        options = [{'label': col, 'value': col} for col in dataframe_cache.columns]
        return options, options[0]['value'], {'display': 'block'}

    @app.callback(
        Output('graph', 'figure'),
        [Input('dropdown', 'value')]
    )
    def update_graph(selected_column):
        if dataframe_cache.empty or not selected_column:
            return {}

        # Si la colonne est catégorique, regrouper par catégories
        if not pd.api.types.is_numeric_dtype(dataframe_cache[selected_column]):
            if 'values' in dataframe_cache.columns:  # Vérifier si une colonne "values" existe pour agrégation
                grouped = dataframe_cache.groupby(selected_column)['values'].sum().reset_index()
                grouped = grouped.sort_values(by='values', ascending=False)
                # Créer le graphique de barres
                fig = px.bar(
                    grouped,
                    x=selected_column,
                    y='values',
                    title=f"Total des valeurs par catégorie dans {selected_column}",
                    text='values',
                    color_discrete_sequence=["#636EFA"]
                )
            else:
                # Afficher un message si pas de colonne "values" pour agrégation
                return px.bar(title="Pas de données numériques pour les catégories.")
        else:
            # Histogramme pour les colonnes numériques
            fig = px.histogram(
                dataframe_cache,
                x=selected_column,
                title=f"Distribution de {selected_column}",
                color_discrete_sequence=["#636EFA"]
            )

        # Mise à jour des options graphiques
        fig.update_layout(
            title={'x': 0.5, 'font': {'size': 24}},
            xaxis_title="Catégories" if not pd.api.types.is_numeric_dtype(dataframe_cache[selected_column]) else "Valeurs",
            yaxis_title="Total des valeurs",
            template="plotly_white"
        )

        return fig

    
    @app.callback(
        Output('graph_pie', 'figure'),
        [Input('dropdown', 'value')]
    )
    def update_pie(selected_column):
        if dataframe_cache.empty or not selected_column:
            return {}

        # Si la colonne est catégorique, regrouper par catégories
        if not pd.api.types.is_numeric_dtype(dataframe_cache[selected_column]):
            if 'values' in dataframe_cache.columns:  # Vérifier l'existence d'une colonne "values"
                grouped = dataframe_cache.groupby(selected_column)['values'].sum().reset_index()
                grouped = grouped.sort_values(by='values', ascending=False)

                # Graphique en secteurs basé sur les totaux
                fig = px.pie(
                    grouped,
                    names=selected_column,
                    values='values',
                    title=f"Répartition des valeurs totales par catégorie dans {selected_column}",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
            else:
                # Si aucune colonne numérique n'est disponible, utiliser les fréquences
                freq = dataframe_cache[selected_column].value_counts().reset_index()
                freq.columns = [selected_column, 'Count']
                
                fig = px.pie(
                    freq,
                    names=selected_column,
                    values='Count',
                    title=f"Répartition des catégories dans {selected_column}",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
        else:
            # Message pour colonne numérique
            fig = px.pie(
                title="Graphique en secteurs non applicable pour les données numériques"
            )

        # Mise à jour des options graphiques
        fig.update_layout(title={'x': 0.5})
        return fig
    @app.callback(
        Output('stats', 'children'),
        [Input('dropdown', 'value')]
    )
    def update_stats(selected_column):
        if dataframe_cache.empty or not selected_column:
            return "Aucune donnée disponible."
        
        # Vérifier si la colonne est numérique
        if pd.api.types.is_numeric_dtype(dataframe_cache[selected_column]):
            stats = dataframe_cache[selected_column].describe()
            return html.Ul([
                html.Li(f"Nombre : {stats['count']}"),
                html.Li(f"Moyenne : {stats['mean']:.2f}"),
                html.Li(f"Médiane : {dataframe_cache[selected_column].median():.2f}"),
                html.Li(f"Ecart-type : {stats['std']:.2f}"),
            ])
        else:
            # Statistiques pour une colonne non numérique
            stats = dataframe_cache[selected_column].describe()
            return html.Ul([
                html.Li(f"Nombre : {stats['count']}"),
                html.Li(f"Valeurs uniques : {stats['unique']}"),
                html.Li(f"Valeur la plus fréquente : {stats['top']}"),
                html.Li(f"Fréquence de la valeur la plus fréquente : {stats['freq']}"),
            ])

# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
options=[{'label': 'All Sites', 'value': 'ALL'}]
for name in spacex_df['Launch Site'].unique():
    options.append({'label': name, 'value': name})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', options=options, value='ALL', searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',   min=min_payload, max=max_payload, step=(max_payload - min_payload) // 10, value=[min_payload, max_payload], marks={int(min_payload): str(min_payload), int(max_payload): str(max_payload)}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),          # <-- write to figure, not children
    Input('site-dropdown', 'value')
)
def draw_success_pie(input_site):
    # pick the right rows
    if input_site != "ALL":
        series = spacex_df.loc[spacex_df['Launch Site'] == input_site, 'class']
        title = f"Success vs Fail – {input_site}"
            # map 1/0 to labels, count, and shape for px.pie
        counts = (series.map({1: 'Success', 0: 'Fail'})       # <-- 0, not 2
                    .value_counts()
                    .rename_axis('Outcome')
                    .reset_index(name='count'))

        fig = px.pie(counts, names='Outcome', values='count', title=title)
    else:
        title = "Total Successful Launches by Launch Site"
        counts = (spacex_df.groupby('Launch Site')['class']
                            .sum()                         # sum of 1/0 = number of successes
                            .reset_index(name='Successes'))

        fig = px.pie(counts, names='Launch Site', values='Successes', title=title)
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def draw_success_scatter(input_site, input_range):
    low, high = input_range  # RangeSlider returns [min, max]

    # Filter by site
    if input_site != "ALL":
        scatter_data = spacex_df.loc[spacex_df['Launch Site'] == input_site, ['Payload Mass (kg)', 'class']]
        title = f"Payload vs Success — {input_site}"
    else:
        scatter_data = spacex_df[['Payload Mass (kg)', 'class']]
        title = "Payload vs Success — All Sites"

    # Filter by payload range (note the & and parentheses)
    mask = ((scatter_data['Payload Mass (kg)'] >= low) &
            (scatter_data['Payload Mass (kg)'] <= high))
    scatter_data = scatter_data.loc[mask]

    fig = px.scatter(
        scatter_data,
        x='Payload Mass (kg)',
        y='class',
        title=title
    )
    # Optional: make y ticks show labels 0/1 clearly
    fig.update_yaxes(tickmode='array', tickvals=[0, 1], ticktext=['Fail', 'Success'])

    return fig

# Run the app
if __name__ == '__main__':
    app.run()

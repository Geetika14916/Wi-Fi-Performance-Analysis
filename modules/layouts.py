from dash import html, dcc

def serve_layout(colors, locations, dates, hours):
    return html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='collection-state', data={'active': False}),


        # 📍 Top-right Start/Stop Button
        html.Div([
            html.Button("Start", id='data-toggle-btn', n_clicks=0, className='small-btn'),
        ], style={
            'position': 'absolute',
            'top': '15px',
            'right': '30px',
            'zIndex': 999
        }),

        # 🧭 Page Header and Tabs Section
        html.Div([
            html.H2("Airport WiFi Performance", style={
                'margin': '0',
                'padding': '20px 0 30px 0',
                'textAlign': 'center',
                'color': colors['text']
            }),

            # Styled Tabs
            dcc.Tabs(
                id='main-tabs',
                value='overview',
                children=[
                    dcc.Tab(label='Overview', value='overview', className='custom-tab', selected_className='custom-tab-selected'),
                    dcc.Tab(label='Run Analysis', value='run_analysis', className='custom-tab', selected_className='custom-tab-selected'),
                    dcc.Tab(label='Trends', value='trends', className='custom-tab', selected_className='custom-tab-selected'),
                    dcc.Tab(label='Heatmap', value='heatmap', className='custom-tab', selected_className='custom-tab-selected'),
                    dcc.Tab(label='Insights', value='insights', className='custom-tab', selected_className='custom-tab-selected'),
                ],
                className='custom-tabs',
                style={'marginBottom': '0'}
            )
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'padding': '20px'
        }),

        # 📦 Main Content Area (varies by tab)
        html.Div(id='tab-content', style={
            'padding': '30px',
            'backgroundColor': colors['background'],
            'minHeight': 'calc(100vh - 150px)',
            'maxWidth': '1400px',
            'margin': '0 auto'
        })
    ])
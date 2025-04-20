# modules/utils.py
dummy_location_to_pixel = {
    "SDB": (100, 150),
    "GEC": (300, 120),
    "ECC": (220, 300),
    "FOODCOURT": (400, 250),
    "LOUNGE": (500, 200)
}


def get_pixel_coords(location_name):
    return dummy_location_to_pixel.get(location_name, (0, 0))

def create_empty_figure(title,colors):
        return {
            'data': [],
            'layout': {
                'title': title,
                'paper_bgcolor': 'white',
                'font': {'color': colors['text']},
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': title,
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 20, 'color': colors['text']}
                }]
            }
        }

    
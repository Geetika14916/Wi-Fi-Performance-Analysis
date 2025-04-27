from modules.config import LOCATION_PIXEL_COORDS


def get_pixel_coords(location_name):
    return LOCATION_PIXEL_COORDS.get(location_name, (0, 0))

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

    
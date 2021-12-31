from .interface import Boilerplate
from ..pages.map import Map as MapPage


class Map(Boilerplate):
    def __init__(self):
        inputs = {
            'map': {
                'datatype': MapPage,
                'validation': None,
                'message': 'Type map name or press enter to get all maps'
            }
        }

        super().__init__(inputs)

    def main(self, user_inputs):
        map: MapPage = user_inputs['map']

        if map.get_searchable_data('map_name') == '':
            map.store_all()

        else:
            map.load_page_data_by('map_name')
            map.store()

class Event:
    def __init__(self, name, hltv_id):
        self.__event_data = {
            'name': name,
            'hltv_id': int(hltv_id)
        }

    def get_name(self):
        return self.__event_data['name']

    def set_name(self, name):
        self.__event_data['name'] = name

    def get_hltv_id(self):
        return self.__event_data['hltv_id']

    def set_hltv_id(self, hltv_id):
        self.__event_data['hltv_id'] = int(hltv_id)

    def load_by_event_data(self, event_data):
        if event_data is None:
            return None

        self.set_name(event_data['name'])
        self.set_hltv_id(event_data['hltv_id'])
    
    def get_event_data(self):
        return self.__event_data
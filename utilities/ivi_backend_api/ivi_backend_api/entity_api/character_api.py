from utilities.ivi_backend_api.ivi_backend_api.base_api import BaseApi


class CharacterApi(BaseApi):
    api = 'character'

    def create_char(self, data):
        response = self._post(self.api, json=data)
        return response["result"]

    def update_char(self, name, char_fields):
        response = self._put('{}/{}'.format(self.api, name), json=char_fields)
        return response["result"]

    def delete_char(self, char_name):
        response = self._delete('{}/{}'.format(self.api, char_name))
        return response["result"]

    def reset_collection(self):
        return self._post('reset')

    def get_all_chars(self):
        response = self._get("characters")
        return response["result"]

    def get_char(self, name):
        response = self._get('{}/{}'.format(self.api, name))
        return response["result"]

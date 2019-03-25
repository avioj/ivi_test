from utilities.ivi_backend_api.ivi_backend_api.base_api import BaseApi
from utilities.ivi_backend_api.ivi_backend_api.model.character import Character
import json
import dataclasses


class CharacterApi(BaseApi):
    api = 'character'

    def create_char(self, data):
        data = dataclasses.asdict(data) if isinstance(data, Character) else data  # TODO: go to python 3.7 or add WA
        response = self._post(self.api, json=data)
        return Character.from_json(json.dumps((response["result"])))

    def update_char(self, name, char_fields):
        char_fields = dataclasses.asdict(char_fields) if isinstance(char_fields, Character) else char_fields  # TODO: go to python 3.7 or add WA
        response = self._put('{}/{}'.format(self.api, name), json=char_fields)
        return response["result"]

    def delete_char(self, char_name):
        response = self._delete('{}/{}'.format(self.api, char_name))
        return response["result"]

    def reset_collection(self):
        return self._post('reset')

    def get_all_chars(self):
        response = self._get("characters")
        return Character.schema().loads(json.dumps(response["result"]), many=True)

    def get_char(self, name):
        response = self._get('{}/{}'.format(self.api, name))
        return response["result"]  # without type becase error return "positive status"

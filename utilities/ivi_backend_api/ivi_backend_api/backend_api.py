from requests import Session


from utilities.ivi_backend_api.ivi_backend_api.entity_api.character_api import CharacterApi


class BackendApi(object):

    def __init__(self, host):
        self.host = host
        self.session = Session()
        self.auth = None
        self.characters = CharacterApi(self.session, host)

    def authorize(self, login, password):
        self.session.auth = (login, password)

    def logout(self):
        self.session.auth = ()
